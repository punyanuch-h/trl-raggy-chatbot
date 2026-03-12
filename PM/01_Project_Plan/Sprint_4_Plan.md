# Sprint 4 Plan: Containerization & Deployment

## Sprint Details
*   **Sprint Goal**: Containerize the Raggy Bot application, migrate secrets to GCP Secret Manager, deploy to Google Cloud Run, and complete the final ISO 29110 release package.
*   **Duration**: 2 Weeks
*   **Methodology**: Agile
*   **Standard**: ISO/IEC 29110 Basic Profile

## Definition of Done (DoD)
A ticket in this sprint is considered "Done" when:
1.  **Container Build**: The Docker image builds successfully and runs locally.
2.  **Secret Integrity**: The application can successfully retrieve secrets from environment variables (provided by Secret Manager in production).
3.  **Deployment Verification**: The API is accessible via a public Cloud Run URL.
4.  **Final Package**: All SI (Software Information) documents and user documentation are updated and archived.

---

## Sprint Backlog

### Ticket 4.1: Containerization (3 Story Points)
*   **Description**: Create a production-ready `Dockerfile` and `.dockerignore`.
*   **Acceptance Criteria**:
    *   `Dockerfile` uses a multi-stage or slim Python 3.12 entry.
    *   `.dockerignore` prevents `.env`, `source/`, and `.venv/` from leaking into the image.
    *   Container starts the FastAPI app via `uvicorn`.

### Ticket 4.2: GCP Secret Manager Integration Plan (3 Story Points)
*   **Description**: Draft the production environment configuration. 
*   **Acceptance Criteria**:
    *   Provisioning guide for GCP Secret Manager.
    *   Update `main.py` or a config loader to handle missing environment variables gracefully.

### Ticket 4.3: Cloud Run Deployment (5 Story Points)
*   **Description**: Deploy the container to Google Cloud Run.
*   **Acceptance Criteria**:
    *   Successful deployment to `us-central1` (or user-specified region).
    *   Public HTTPS endpoint is functional.

### Ticket 4.4: Final Release Audit & User Manual (5 Story Points)
*   **Description**: Complete the ISO 29110 Release Report and the final User Manual.
*   **Acceptance Criteria**:
    *   `SI/06_User_Manual/` updated.
    *   `SI/07_Product_Release/Final_Release_Report.md` completed.

---

## Resource Mapping
*   **Documentation**: ISO 29110 Repository (`SI/` folder)
*   **Source Code**: `Dockerfile`, `.dockerignore`
*   **Platform**: Google Cloud Platform (GCloud SDK)
