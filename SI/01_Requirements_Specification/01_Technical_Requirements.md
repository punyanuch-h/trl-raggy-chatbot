# Technical Requirements Specification: Raggy Bot

## 1. Core Architecture Stack (Finalized)
*   **Operating Language**: Python
*   **Web Framework**: FastAPI
*   **LLM Provider**: OpenAI
*   **Vector Database**: Pinecone (Serverless Cloud DB)
    *   *Justification*: Chosen specifically for exceptional cloud-native free tier capacity (handles up to 100 users efficiently) without local infrastructure management overhead.
*   **Orchestration Library**: LangChain
*   **Testing Suite**: `pytest`

## 2. API Specifications & Security
*   **Local Execution Environment**: The API will be served via the Uvicorn ASGI server and explicitly bound to **Port `8001`** to avoid conflict with your existing standard backend `8080` and frontend `3000` ports.
*   **Endpoint Route**: The system MUST implement precisely one primary operational endpoint exposed entirely via POST at the path `/raggy/trl`.
*   **API Security (Authentication)**: Since Raggy Bot is a headless microservice, it must be secured so public internet users cannot query it directly and waste your OpenAI credits:
    *   **Recommended Approach (Service-to-Service)**: If your Backend (`8080`) is the one calling Raggy Bot, we can just use a strong, static `X-API-Key` header.
    *   **Alternative Approach (Frontend Direct)**: If your Frontend (`3000`) is calling Raggy Bot directly, Raggy Bot must validate the **JWT Token** sent in the `Authorization: Bearer <token>` header to confirm the user is logged into your main system.
*   **API Payload Rules**: The system expects incoming JSON POST bodies providing the inquiry strictly mapped using two parameters:
    *   `query` (string): The researcher's question.
    *   `role` (string): The identity of the caller (`researcher` or `admin`).


## 3. Data Pipeline & Privacy Control (RBAC)
*   **Document Ingestion**: The system must extract chunks from raw PDF files dropped manually (or programmatically) into predefined folders:
    *   `source/` (General documents accessible to everyone)
    *   `source/private/` (Confidential documents)
*   **Filter Logic**: The system must rely on strict metadata filtering built strictly into the **Pinecone Vector Search query layer**.
    *   When embedding a PDF from the `source/private/` folder into Pinecone, it must be tagged with restricted metadata (e.g., `role: admin`). 
    *   When the API handles a request mapped to a `researcher`, the Vector search must explicitly exclude any chunks matching that restricted metadata *before* supplying context to the OpenAI LLM. This guarantees no data leakage via hallucination.

## 4. Evaluation & TDD Directives (ISO 29110)
*   **Deterministic Elements**: Pipeline components (PDF extraction, text chunking algorithms, JSON endpoint serialization) must achieve "Green" state via unit testing in `SI/04_Test_Cases_and_Procedures/` directly prior to logic implementation.
*   **Non-Deterministic Outcomes**: The system generative language responses must leverage specialized test frameworks designed explicitly for LLM validation (such as Ragas or TruLens) assessing Faithfulness and Answer Relevance.
