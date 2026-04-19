import os
import base64
import jwt
from fastapi import FastAPI, Request, Response, Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import sys
import importlib.metadata
from dotenv import load_dotenv

# Load local environment variables for localhost runs
load_dotenv()


# LangChain Imports
from langchain_openai import ChatOpenAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from rag_retriever import get_retriever
from rag_prompts import get_trl_prompt
from pinecone_manager import PineconeManager
from response_formatter import format_answer_markdown
from metadata_store import DEFAULT_MODEL_NAME, build_metadata_record, generate_request_id, get_metadata_store_from_env
from assessment.response_templates import get_response_message, get_response_title
from assessment.conversation import run_assessment_turn
from assessment.session_state import InMemoryAssessmentSessionStore, generate_session_id
from source_qa import answer_query_from_source
from agents.intent_router import IntentDecision, route_trl_intent
from agents.orchestrator import orchestrate_query
from agents.qa_agent import answer_general_qa
from language_support import detect_language, resolve_response_language, localize_missing_evidence

app = FastAPI(
    title="Raggy Bot API",
    description="API Endpoint for TRL Retrieval-Augmented Generation",
    version="1.0.0"
)

# CORS Setup - Whitelisting Frontend Domain
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def build_query_response(answer_text: str, mode: str = "qa", language: str = "th") -> dict:
    """Return the canonical markdown response payload."""
    return {
        "answer_markdown": format_answer_markdown(answer_text, title=get_response_title(mode, language=language)),
        "language": language,
    }


def safe_route_trl_intent(query: str) -> IntentDecision:
    """Prefer a safe QA fallback if the router cannot classify the request."""
    try:
        return route_trl_intent(query)
    except Exception as router_error:
        print(f"[WARN] Intent routing failed: {router_error}")
        return IntentDecision(
            intent="general_qa",
            needs_clarification=False,
            rationale="router_fallback_after_error",
        )


def build_safe_qa_answer(
    query: str,
    rag_answer: str | None,
    prefer_technical_error: bool = False,
    retrieval_status: str = "completed",
    language: str = "th",
) -> str:
    """Keep QA responses usable even when retrieval or orchestration is degraded."""
    qa_response = answer_general_qa(
        query=query,
        rag_answer=rag_answer,
        retrieval_status=retrieval_status,
        language=language,
    )
    if qa_response.source == "qa_fallback" and prefer_technical_error:
        return get_response_message("technical_error", mode="qa", language=language)
    return qa_response.answer_text


def try_source_qa_answer(query: str, language: str = "th") -> str | None:
    """Return a deterministic local-source QA answer when the query is supported."""
    try:
        source_answer = answer_query_from_source(query, language=language)
        if source_answer and str(source_answer).strip():
            print("[SourceQA] Answered deterministic query from local source/")
            return source_answer
    except Exception as source_error:
        print(f"[WARN] Source QA failed: {source_error}")
    return None

# -------------------------------------------------------------
# EXCEPTION ENGINE: Polite Error Handling System (Ticket 3)
# -------------------------------------------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Catches invalid payloads (e.g. users uploading files instead of text or sending empty JSON).
    Instead of throwing a technical 422 Unprocessable Entity error, it returns a polite 200 OK.
    """
    return JSONResponse(
        status_code=200,
        content=build_query_response(
            get_response_message("validation_error", mode="qa")
        ),
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Prevents data leakage on Auth failures (Ticket 4).
    Intercepts 401 Unauthorized errors and returns a soft 200 OK conversational apology.
    """
    if exc.status_code == 401:
        return JSONResponse(
            status_code=200,
            content=build_query_response(
                get_response_message("auth_error", mode="qa")
            ),
        )
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

# -------------------------------------------------------------
# SECURITY MIDDLEWARE (Ticket 4)
# -------------------------------------------------------------
security = HTTPBearer(auto_error=False)

class UserRole(BaseModel):
    role: str
    user_id: str
    user_email: str | None = None
    client_id: str | None = None
    client_name: str | None = None
    is_temp: bool = False


def _get_env_public_key_for_kid(kid: str | None) -> str | None:
    if kid:
        kid_env_name = f"JWT_PUBLIC_KEY_{str(kid).upper().replace('-', '_')}"
        if os.environ.get(kid_env_name):
            return os.environ.get(kid_env_name)
    return os.environ.get("JWT_PUBLIC_KEY")


def _load_public_key_material(kid: str | None) -> str:
    public_key = _get_env_public_key_for_kid(kid)
    public_key_file = os.environ.get("JWT_PUBLIC_KEY_FILE")

    if public_key:
        normalized_key = public_key.strip().replace("\\n", "\n")
        if "BEGIN PUBLIC KEY" in normalized_key:
            return normalized_key
        try:
            decoded_key = base64.b64decode(normalized_key).decode("utf-8")
            decoded_key = decoded_key.strip()
            if "BEGIN PUBLIC KEY" in decoded_key:
                return decoded_key
        except Exception:
            pass
        return normalized_key
    if public_key_file:
        with open(public_key_file, "r", encoding="utf-8") as key_file:
            return key_file.read()
    raise HTTPException(status_code=401, detail="Missing RSA verification key")


def _get_jwt_decode_kwargs(token: str) -> dict:
    jwt_audience = os.environ.get("JWT_AUDIENCE")
    jwt_issuer = os.environ.get("JWT_ISSUER")
    header = jwt.get_unverified_header(token)
    algorithm = header.get("alg")
    kid = header.get("kid")

    if algorithm != "RS256":
        raise HTTPException(status_code=401, detail="Unsupported Token Algorithm")
    key = _load_public_key_material(kid)

    decode_kwargs = {
        "key": key,
        "algorithms": ["RS256"],
        "options": {
            "verify_aud": bool(jwt_audience),
        },
    }

    if jwt_audience:
        decode_kwargs["audience"] = jwt_audience
    if jwt_issuer:
        decode_kwargs["issuer"] = jwt_issuer

    return decode_kwargs

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Extracts JWT from header, verifies mathematically, and determines role safely."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing Token")
    
    token = credentials.credentials
    
    try:
        # Decode signed JWT and keep standard time-based claims enforced.
        payload = jwt.decode(token, **_get_jwt_decode_kwargs(token))
        
        # Extracts role, defaulting to researcher if missing or malformed to stay safe
        role = payload.get("role", "researcher")
        if role not in ["admin", "researcher"]:
            role = "researcher" 

        user_id = str(payload.get("sub") or payload.get("user_id") or "unknown")
        user_email = payload.get("user_email")
        client_id = payload.get("client_id")
        client_name = payload.get("client_name")
        is_temp = bool(payload.get("is_temp", False))

        return UserRole(
            role=role,
            user_id=user_id,
            user_email=user_email,
            client_id=client_id,
            client_name=client_name,
            is_temp=is_temp,
        )
    except Exception as e:
        # Catches ExpiredSignatureError, DecodeError, etc.
        print(f"[DEBUG] Auth Failed with token {token[:10]}... Error: {e}")
        raise HTTPException(status_code=401, detail="Invalid Token")

# -------------------------------------------------------------
# PRIMARY ROUTERS
# -------------------------------------------------------------
class QueryRequest(BaseModel):
    query: str
    session_id: str | None = None
    candidate_level: int | None = None
    response_language: str | None = None

class AssessmentResultPayload(BaseModel):
    candidate_level: int
    matched_level: int
    decision_status: str
    reasoning_summary: str


class QueryResponse(BaseModel):
    answer_markdown: str
    language: str
    session_id: str | None = None
    mode: str | None = None
    assessment_result: AssessmentResultPayload | None = None
    missing_evidence: list[dict[str, str]] | None = None
    next_question: str | None = None

class MetadataRecord(BaseModel):
    request_id: str
    session_id: str | None = None
    user_id: str
    role: str
    timestamp: str
    response_status: str
    route_path: str
    model_name: str
    workflow_mode: str | None = None
    decision_status: str | None = None


class MetadataRecordListResponse(BaseModel):
    records: list[MetadataRecord]


class PineconeConnectionResponse(BaseModel):
    connected: bool
    index_name: str
    host: str | None = None
    dimension: int | None = None
    metric: str | None = None
    ready: bool
    state: str | None = None
    total_vector_count: int
    namespaces: dict[str, int]


def get_metadata_store():
    return get_metadata_store_from_env()


ASSESSMENT_SESSION_STORE = InMemoryAssessmentSessionStore()


def get_assessment_session_store() -> InMemoryAssessmentSessionStore:
    return ASSESSMENT_SESSION_STORE


def require_admin_user(user: UserRole) -> UserRole:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return user


@app.post("/raggy/trl", response_model=QueryResponse, response_model_exclude_none=True)
async def process_trl_query(
    request: QueryRequest,
    response: Response,
    http_request: Request,
    user: UserRole = Security(get_current_user),
):
    """
    Accepts a single user query regarding TRL levels.
    Processes the query through the LangChain RAG chain with RBAC enforcement.
    """
    try:
        request_id = http_request.headers.get("X-Request-ID") or generate_request_id()
        session_id = request.session_id or http_request.headers.get("X-Session-ID")
        query_language = detect_language(request.query)
        response_language = resolve_response_language(request.query, request.response_language)
        response.headers["X-Request-ID"] = request_id

        assessment_session_store = get_assessment_session_store()
        decision = safe_route_trl_intent(request.query)
        existing_assessment_session = assessment_session_store.get(session_id) if session_id else None
        if decision.intent == "trl_assessment" or existing_assessment_session is not None:
            try:
                active_session_id = session_id or generate_session_id()
                assessment_turn = run_assessment_turn(
                    request.query,
                    session_id=active_session_id,
                    store=assessment_session_store,
                    candidate_level=request.candidate_level,
                    language=response_language,
                )
                workflow_mode = "assessment"
                decision_status = assessment_turn.decision_status
                localized_missing_evidence = localize_missing_evidence(assessment_turn.missing_evidence, response_language)
                response_payload = QueryResponse(
                    answer_markdown=format_answer_markdown(
                        assessment_turn.answer_text,
                        title=get_response_title("assessment", language=response_language),
                    ),
                    language=response_language,
                    session_id=assessment_turn.session_id,
                    mode=workflow_mode,
                    assessment_result=AssessmentResultPayload(
                        candidate_level=assessment_turn.candidate_level,
                        matched_level=assessment_turn.matched_level,
                        decision_status=assessment_turn.decision_status,
                        reasoning_summary=assessment_turn.reasoning_summary,
                    ),
                    missing_evidence=localized_missing_evidence,
                    next_question=assessment_turn.next_question,
                )
            except Exception as assessment_error:
                print(f"[WARN] Assessment workflow failed: {assessment_error}")
                workflow_mode = "assessment"
                decision_status = "technical_fallback"
                response_payload = QueryResponse(
                    answer_markdown=format_answer_markdown(
                        get_response_message("technical_error", mode="assessment", language=response_language),
                        title=get_response_title("assessment", language=response_language),
                    ),
                    language=response_language,
                    session_id=session_id,
                    mode=workflow_mode,
                )
        else:
            rag_answer = try_source_qa_answer(request.query, language=response_language)
            rag_failed = False
            retrieval_status = "completed" if rag_answer else "not_attempted"
            if not rag_answer:
                try:
                    llm = ChatOpenAI(
                        model=DEFAULT_MODEL_NAME,
                        temperature=0,
                        base_url=os.environ.get("OPENAI_BASE_URL")
                    )
                    retriever = get_retriever(role=user.role)
                    prompt = get_trl_prompt()

                    combine_docs_chain = create_stuff_documents_chain(llm, prompt)
                    rag_chain = create_retrieval_chain(retriever, combine_docs_chain)
                    rag_response = rag_chain.invoke({"input": request.query})
                    rag_answer = rag_response.get("answer")
                    retrieval_status = "empty_answer" if not (rag_answer and str(rag_answer).strip()) else "completed"
                except Exception as rag_error:
                    rag_failed = True
                    retrieval_status = "retrieval_failed"
                    print(f"[WARN] QA retrieval failed: {rag_error}")

            if not (rag_answer and str(rag_answer).strip()):
                rag_answer = try_source_qa_answer(request.query, language=response_language)
                if rag_answer:
                    retrieval_status = "completed"

            try:
                workflow_result = orchestrate_query(request.query, rag_answer=rag_answer, language=response_language)
                workflow_mode = workflow_result.mode
                decision_status = "clarification_requested" if workflow_result.needs_clarification else "completed"
                response_payload = QueryResponse(
                    answer_markdown=format_answer_markdown(
                        workflow_result.answer_text,
                        title=get_response_title(workflow_result.mode, language=response_language),
                    ),
                    language=response_language,
                    mode=workflow_result.mode,
                )
            except Exception as orchestration_error:
                print(f"[WARN] QA orchestration failed: {orchestration_error}")
                workflow_mode = "qa"
                decision_status = "technical_fallback" if rag_failed else "completed_with_fallback"
                fallback_answer = build_safe_qa_answer(
                    request.query,
                    rag_answer=rag_answer,
                    prefer_technical_error=rag_failed,
                    retrieval_status=retrieval_status,
                    language=response_language,
                )
                response_payload = QueryResponse(
                    answer_markdown=format_answer_markdown(
                        fallback_answer,
                        title=get_response_title("qa", language=response_language),
                    ),
                    language=response_language,
                    mode=workflow_mode,
                )

        print(
            f"[ORCHESTRATOR] request_id={request_id} intent={decision.intent} "
            f"mode={workflow_mode} status={decision_status} query_language={query_language} response_language={response_language}"
        )

        metadata_store = get_metadata_store()
        if metadata_store:
            try:
                metadata_store.save_record(
                    build_metadata_record(
                        user_id=user.user_id,
                        role=user.role,
                        route_path=str(http_request.url.path),
                        request_id=request_id,
                        session_id=response_payload.session_id or session_id,
                        response_status="success",
                        model_name=DEFAULT_MODEL_NAME,
                        workflow_mode=workflow_mode,
                        decision_status=decision_status,
                    )
                )
            except Exception as metadata_error:
                print(f"[WARN] Metadata persistence failed for {request_id}: {metadata_error}")

        return response_payload

    except Exception as e:
        # Log error for admin oversight
        print(f"[Internal Error] RAG Chain failure: {str(e)}")
        # Return polite apology instead of raw crash (Ticket 3 constraint)
        return QueryResponse(
            **build_query_response(
                get_response_message("technical_error", mode="qa")
            )
        )


@app.get("/internal/metadata/sessions/{session_id}", response_model=MetadataRecordListResponse)
async def get_metadata_by_session(
    session_id: str,
    user: UserRole = Security(get_current_user),
):
    require_admin_user(user)
    metadata_store = get_metadata_store()
    if not metadata_store:
        raise HTTPException(status_code=503, detail="Metadata store unavailable")
    return MetadataRecordListResponse(records=metadata_store.get_records_by_session(session_id))


@app.get("/internal/metadata/requests", response_model=MetadataRecordListResponse)
async def get_recent_metadata_records(
    limit: int = 20,
    user: UserRole = Security(get_current_user),
):
    require_admin_user(user)
    metadata_store = get_metadata_store()
    if not metadata_store:
        raise HTTPException(status_code=503, detail="Metadata store unavailable")
    bounded_limit = max(1, min(limit, 100))
    return MetadataRecordListResponse(records=metadata_store.list_recent_records(limit=bounded_limit))


@app.get("/internal/pinecone/connection", response_model=PineconeConnectionResponse)
async def get_pinecone_connection_report(
    user: UserRole = Security(get_current_user),
):
    require_admin_user(user)
    manager = PineconeManager()
    report = manager.get_connection_report()
    return PineconeConnectionResponse(connected=True, **report)


if __name__ == "__main__":
    # Get port from environment variable (default to 8080 for Cloud Run)
    port = int(os.environ.get("PORT", 8080))
    # In production/cloud, we bind to 0.0.0.0
    host = "0.0.0.0" if os.environ.get("K_SERVICE") else "127.0.0.1"
    
    # Check for mandatory secrets in production
    if os.environ.get("K_SERVICE"):
        required_vars = ["OPENAI_API_KEY", "PINECONE_API_KEY"]
        for var in required_vars:
            if not os.environ.get(var):
                print(f"[CRITICAL] Missing mandatory environment variable: {var}")
        if not any(
            [
                os.environ.get("JWT_PUBLIC_KEY"),
                os.environ.get("JWT_PUBLIC_KEY_FILE"),
            ]
        ):
            print("[CRITICAL] Missing JWT verification configuration: set JWT_PUBLIC_KEY/JWT_PUBLIC_KEY_FILE for RS256")
    
    uvicorn.run(app, host=host, port=port)
