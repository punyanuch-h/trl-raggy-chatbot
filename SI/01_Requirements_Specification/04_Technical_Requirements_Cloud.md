# Technical Requirements Specification: Raggy Bot (Version 4 - Cloud Deployment)

## 1. Cloud Infrastructure Stack
*   **Platform**: Google Cloud Platform (GCP).
*   **Execution Environment**: Google Cloud Run (Fully Managed Serverless).
*   **Port Configuration**: The application must listen on Port **8080** to align with Cloud Run's default routing.
*   **Scaling Policy**:
    *   *Min Instances*: 0 (to optimize costs during pilot).
    *   *Max Instances*: 10 (sufficient for the 100-user requirement).
    *   *Concurrency*: 80 requests per instance.

## 2. Production Secret Management
*   **Constraint**: Standard `.env` files are strictly prohibited in the production container image to prevent credential leakage.
*   **Implementation**:
    *   Sensitive keys (`OPENAI_API_KEY`, `PINECONE_API_KEY`, `JWT_SECRET`) must be stored in **GCP Secret Manager**.
    *   The Cloud Run service must mount these secrets as environment variables at runtime.
    *   The application must fail gracefully with a clear log entry if mandatory secrets are missing.

## 3. Containerization (Docker)
*   **Base Image**: `python:3.12-slim` (to minimize attack surface and image size).
*   **Optimization**: Use `.dockerignore` to exclude local artifacts, tests, and documentation.
*   **Entrypoint**: Use `python main.py` or `uvicorn main:app --host 0.0.0.0 --port 8080` (as defined in `main.py`).

## 4. Network & Security
*   **Protocol**: HTTPS only (enforced by Google Cloud Run).
*   **CORS**: Update whitelist to include the production frontend domain (to be provided during deployment).
*   **Ingestion Safety**: The ingestion CLI (`reindex.py`) continues to run in a trusted local environment; only the resulting vectors are transmitted to the cloud-hosted Pinecone index.

## 5. Persistence & State
*   **Statelessness**: The API must remain entirely stateless.
*   **Vector Database**: Connectivity must be established securely to the serverless Pinecone instance via API Key.

---
**Approved for Sprint 5.**
