# Technical Requirements Specification: Raggy Bot (Version 3)

## 1. Core Architecture Stack (Finalized)
*   **Operating Language**: Python
*   **Web Framework**: FastAPI
*   **LLM Provider**: OpenAI
*   **Vector Database**: Pinecone (Serverless Cloud DB)
    *   *Dimensions Rule*: Pinecone must be configured strictly to expect `1536` dimension vectors to align exactly with OpenAI's embedding model.
*   **Embedding Model**: OpenAI `text-embedding-3-small`
*   **Orchestration Library**: LangChain
*   **Testing Suite**: `pytest`

## 2. API Security, CORS, & JWT Decoding
*   **API Execution**: The Uvicorn ASGI server must strictly bind to **Port `8001`**. 
*   **CORS Configuration**: FastAPI must configure a CORS Middleware block to explicitly whitelist incoming API traffic originating specifically from the Frontend UI domain (`http://localhost:3000`), thereby preventing browser security blocks.
*   **Endpoint Route**: The system implements precisely one operational conversational endpoint exposed entirely via POST at the path `/raggy/trl`.
*   **API JWT Handling**: The Frontend Client (`3000`) is the direct consumer of this microservice. 
    *   The client MUST send the user's **JWT Token** inside the `Authorization: Bearer <token>` HTTP header.
    *   Raggy Bot will decode this JWT token to authenticate the user and establish their role. 
    *   **The Secret Strategy**: Raggy will use a shared `JWT_SECRET` key securely supplied via a local `.env` file to mathematically verify the token signature.
    *   **Payload Fallback**: Raggy expects the JWT payload to contain a `role` key (i.e. `{"role": "admin"}`). If the decoder succeeds but the key is missing or unrecognizable, the system must immediately and safely downgrade the user to the `researcher` permissions level.

## 3. Safe Request Exception Engine
*   **Graceful Exception Catching Constraint**: The system expects incoming JSON POST bodies or multipart/form data containing a text `query` string. No chat history will be passed.
*   If the frontend mistakenly sends an image, if validation fails, or if the server timeouts, **FastAPI must not expose HTTP error status codes or JSON stack traces.**
    *   FastAPI must leverage specialized overriding Exception Handlers to return `HTTP 200 OK` or `HTTP 401 Unauthorized` responses containing a predefined conversational payload:
    *   *Input Example Response*: `{"answer": "I'm sorry, but I am currently only equipped to answer text-based questions. Please type out your question and I would be happy to help!"}`
    *   *Security Error Example Response*: `{"answer": "I apologize, but I couldn't securely verify your access session. Could you please try logging in again?"}`

## 4. LLM Generation Directives (Healthcare & Education Focus)
*   **Prompt Engineering Structure**: The system prompt injected via LangChain MUST strictly define the persona. Due to its deployment within the healthcare and education systems, the prompt must constrain OpenAI to only generate tokens using an **extremely polite, supportive, patient, and professional tone**.

## 5. Data Pipeline & Privacy Control (RBAC)
*   **Document Ingestion**: The system extracts chunks from root PDF files in two predefined folders:
    *   `source/` (General documents accessible to everyone)
    *   `source/private/` (Confidential documents)
*   **Filter Logic**: The system must rely on strict metadata filtering built directly into the **Pinecone Vector Search query layer**.
    *   When embedding a PDF from the `source/private/` folder into Pinecone, it must be tagged with restricted metadata (e.g., `role: admin`). 
    *   When the API handles a request where the JWT translates the user to an identity of a `researcher`, the Vector search must explicitly exclude any chunks matching that restricted metadata *before* supplying context to the OpenAI LLM. 

## 6. Evaluation & TDD Directives (ISO 29110)
*   **Deterministic Elements**: Pipeline components (PDF extraction, JWT Decoding, JSON/Exception serialization, CORS checks) must achieve "Green" state via `pytest` unit testing in `SI/04_Test_Cases_and_Procedures/` directly prior to feature coding.
*   **Non-Deterministic Outcomes**: generative language responses must leverage specialized test frameworks for LLM validation (such as Ragas or TruLens) assessing Politeness, Faithfulness, and Answer Relevance.
