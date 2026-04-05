import os
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
from response_formatter import format_answer_markdown
from metadata_store import DEFAULT_MODEL_NAME, build_metadata_record, generate_request_id, get_metadata_store_from_env

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


def build_query_response(answer_text: str) -> dict:
    """Return the canonical markdown response payload."""
    return {
        "answer_markdown": format_answer_markdown(answer_text),
    }

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
            "I'm sorry, but I am currently only equipped to answer text-based questions. Please type out your question and I would be happy to help!"
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
                "I apologize, but I couldn't securely verify your access session. Could you please try logging in again?"
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

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Extracts JWT from header, verifies mathematically, and determines role safely."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing Token")
    
    token = credentials.credentials
    jwt_secret = os.environ.get("JWT_SECRET", "default_secret")
    
    try:
        # Tries to decode via symmetric key
        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        
        # Extracts role, defaulting to researcher if missing or malformed to stay safe
        role = payload.get("role", "researcher")
        if role not in ["admin", "researcher"]:
            role = "researcher" 

        user_id = str(payload.get("sub") or payload.get("user_id") or "unknown")

        return UserRole(role=role, user_id=user_id)
    except Exception as e:
        # Catches ExpiredSignatureError, DecodeError, etc.
        print(f"[DEBUG] Auth Failed with token {token[:10]}... Error: {e}")
        raise HTTPException(status_code=401, detail="Invalid Token")

# -------------------------------------------------------------
# PRIMARY ROUTERS
# -------------------------------------------------------------
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer_markdown: str

class MetadataRecord(BaseModel):
    request_id: str
    session_id: str | None = None
    user_id: str
    role: str
    timestamp: str
    response_status: str
    route_path: str
    model_name: str


class MetadataRecordListResponse(BaseModel):
    records: list[MetadataRecord]


def get_metadata_store():
    return get_metadata_store_from_env()


def require_admin_user(user: UserRole) -> UserRole:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return user


@app.post("/raggy/trl", response_model=QueryResponse)
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
        session_id = http_request.headers.get("X-Session-ID")
        response.headers["X-Request-ID"] = request_id

        # 1. Initialize the components
        llm = ChatOpenAI(
            model=DEFAULT_MODEL_NAME,
            temperature=0,
            base_url=os.environ.get("OPENAI_BASE_URL")
        )
        retriever = get_retriever(role=user.role)
        prompt = get_trl_prompt()

        # 2. Build the RAG chain
        combine_docs_chain = create_stuff_documents_chain(llm, prompt)
        rag_chain = create_retrieval_chain(retriever, combine_docs_chain)

        # 3. Execute the chain
        rag_response = rag_chain.invoke({"input": request.query})

        metadata_store = get_metadata_store()
        if metadata_store:
            try:
                metadata_store.save_record(
                    build_metadata_record(
                        user_id=user.user_id,
                        role=user.role,
                        route_path=str(http_request.url.path),
                        request_id=request_id,
                        session_id=session_id,
                        response_status="success",
                        model_name=DEFAULT_MODEL_NAME,
                    )
                )
            except Exception as metadata_error:
                print(f"[WARN] Metadata persistence failed for {request_id}: {metadata_error}")

        return QueryResponse(**build_query_response(rag_response["answer"]))

    except Exception as e:
        # Log error for admin oversight
        print(f"[Internal Error] RAG Chain failure: {str(e)}")
        # Return polite apology instead of raw crash (Ticket 3 constraint)
        return QueryResponse(
            **build_query_response(
                "I'm sorry, I encountered a technical difficulty while processing your request. Please try again in a few moments."
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


if __name__ == "__main__":
    # Get port from environment variable (default to 8080 for Cloud Run)
    port = int(os.environ.get("PORT", 8080))
    # In production/cloud, we bind to 0.0.0.0
    host = "0.0.0.0" if os.environ.get("K_SERVICE") else "127.0.0.1"
    
    # Check for mandatory secrets in production
    if os.environ.get("K_SERVICE"):
        required_vars = ["OPENAI_API_KEY", "PINECONE_API_KEY", "JWT_SECRET"]
        for var in required_vars:
            if not os.environ.get(var):
                print(f"[CRITICAL] Missing mandatory environment variable: {var}")
    
    uvicorn.run(app, host=host, port=port)
