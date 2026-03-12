import os
import jwt
from fastapi import FastAPI, Request, Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import sys
import importlib.metadata

# Debugging the environment


# LangChain Imports
from langchain_openai import ChatOpenAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from rag_retriever import get_retriever
from rag_prompts import get_trl_prompt

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
        content={
            "answer": "I'm sorry, but I am currently only equipped to answer text-based questions. Please type out your question and I would be happy to help!"
        }
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
            content={
                "answer": "I apologize, but I couldn't securely verify your access session. Could you please try logging in again?"
            }
        )
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

# -------------------------------------------------------------
# SECURITY MIDDLEWARE (Ticket 4)
# -------------------------------------------------------------
security = HTTPBearer(auto_error=False)

class UserRole(BaseModel):
    role: str

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
            
        return UserRole(role=role)
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
    answer: str

@app.post("/raggy/trl", response_model=QueryResponse)
async def process_trl_query(request: QueryRequest, user: UserRole = Security(get_current_user)):
    """
    Accepts a single user query regarding TRL levels.
    Processes the query through the LangChain RAG chain with RBAC enforcement.
    """
    try:
        # 1. Initialize the components
        llm = ChatOpenAI(
            model="gpt-4o-mini", 
            temperature=0,
            base_url=os.environ.get("OPENAI_BASE_URL")
        )
        retriever = get_retriever(role=user.role)
        prompt = get_trl_prompt()

        # 2. Build the RAG chain
        combine_docs_chain = create_stuff_documents_chain(llm, prompt)
        rag_chain = create_retrieval_chain(retriever, combine_docs_chain)

        # 3. Execute the chain
        response = rag_chain.invoke({"input": request.query})

        return QueryResponse(answer=response["answer"])

    except Exception as e:
        # Log error for admin oversight
        print(f"[Internal Error] RAG Chain failure: {str(e)}")
        # Return polite apology instead of raw crash (Ticket 3 constraint)
        return QueryResponse(
            answer="I'm sorry, I encountered a technical difficulty while processing your request. Please try again in a few moments."
        )


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
