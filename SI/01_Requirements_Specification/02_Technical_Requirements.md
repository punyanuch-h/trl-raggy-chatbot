# Technical Requirements Specification: Raggy Bot (Version 2)

## 1. Core Architecture Stack (Finalized)
*   **Operating Language**: Python
*   **Web Framework**: FastAPI
*   **LLM Provider**: OpenAI
*   **Vector Database**: Pinecone (Serverless Cloud DB)
    *   *Justification*: Handles up to 100 users efficiently; serverless.
*   **Orchestration Library**: LangChain
*   **Testing Suite**: `pytest`

## 2. API Specifications & Security
*   **Execution Environment**: The API will be served via the Uvicorn ASGI server and explicitly bound to **Port `8001`**. This completely avoids conflict with your existing backend API serving port `8080` and frontend serving port `3000`.
*   **Endpoint Route**: The system implements precisely one operational conversational endpoint exposed entirely via POST at the path `/raggy/trl`.
*   **API Security (Direct Frontend Auth)**: The Frontend Client (port `3000`) is the direct consumer of this microservice. 
    *   The client MUST send the user's **JWT Token** inside the `Authorization: Bearer <token>` HTTP header on every request.
    *   Raggy Bot will decode this JWT token to authenticate the user's validity and determine their identity role (`researcher` or `admin`).

## 3. Request Payloads & Validation Engine
*   **Text Processing Rule**: The system expects incoming JSON POST bodies or multipart/form data but exclusively processes text input.
*   **Graceful Exception Catching**: If the frontend mistakenly (or purposefully) sends a file, image, or non-text binary data, FastAPI must intercept the validation error (HTTP 422 Unprocessable Entity, etc).
    *   Instead of returning a JSON error stack trace, FastAPI must leverage a specialized Exception Handler to return HTTP 200 OK paired with a predefined conversational payload:
    *   *Response Example*: `{"answer": "I'm sorry, but I am currently only equipped to answer text-based questions. Please type out your question and I would be happy to help!"}`

## 4. LLM Generation Directives (Healthcare & Education Focus)
*   **Prompt Engineering Structure**: The system prompt injected via LangChain MUST strictly define the persona. Due to its deployment within the healthcare and education systems, the prompt must constrain OpenAI to only generate tokens using an **extremely polite, supportive, and professional tone**.

## 5. Data Pipeline & Privacy Control (RBAC)
*   **Document Ingestion**: The system extracts chunks from root PDF files in two predefined folders:
    *   `source/` (General documents accessible to everyone)
    *   `source/private/` (Confidential documents)
*   **Filter Logic**: The system must rely on strict metadata filtering built directly into the **Pinecone Vector Search query layer**.
    *   When embedding a PDF from the `source/private/` folder into Pinecone, it must be tagged with restricted metadata (e.g., `role: admin`). 
    *   When the API handles a request where the JWT token translates the user to an identity of a `researcher`, the Vector search must explicitly exclude any chunks matching that restricted metadata *before* supplying context to the OpenAI LLM. This prevents hallucination data leakage.

## 6. Evaluation & TDD Directives (ISO 29110)
*   **Deterministic Elements**: Pipeline components (PDF extraction, JWT Decoding, JSON/Exception serialization) must achieve "Green" state via `pytest` unit testing in `SI/04_Test_Cases_and_Procedures/` directly prior to feature coding.
*   **Non-Deterministic Outcomes**: The system generative language responses must leverage specialized test frameworks for LLM validation (such as Ragas or TruLens) assessing Politeness, Faithfulness, and Answer Relevance.
