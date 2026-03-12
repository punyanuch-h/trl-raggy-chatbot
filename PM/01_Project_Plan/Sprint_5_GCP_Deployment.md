# Sprint 5 Plan: Production Infrastructure & Cloud Deployment

## 📋 Sprint Overview
*   **Sprint Goal**: Securely transition the Raggy Bot microservice from a local development environment to an ISO 29110-compliant production environment on **Google Cloud Run**.
*   **Duration**: 1 Week
*   **Methodology**: Agile (Scrum)
*   **Compliance Standard**: ISO/IEC 29110 Basic Profile
*   **Current Status**: Application logic finalized (v1.0); ready for infrastructure provisioning.

---

## 🛠️ Prerequisites (Pre-Sprint Setup)
*   **GCP SDK**: Google Cloud CLI (`gcloud`) must be installed and authenticated (`gcloud auth login`).
*   **Docker**: Docker Desktop or Engine must be running for local builds.
*   **Permissions**: The user must have `Owner` or `Editor` access to the target GCP Project.

---

## 🏗️ Definition of Done (DoD)
A ticket is considered "Done" when:
1.  **Infrastructure Verified**: The GCP resources (Cloud Run, Artifact Registry, Secret Manager) are provisioned.
2.  **Zero-Leak Security**: No secrets exist in the source code or local `.env` files within the container.
3.  **Endpoint Accessibility**: The API returns a valid response over public HTTPS.
4.  **RBAC Verification**: Successful confirmation that the "researcher" role cannot access "admin" documents in the cloud environment.
5.  **Documentation**: `SI/07_Product_Release/` updated with the deployment log.

---

## 🎟️ Sprint Backlog

### Ticket 5.1: GCP Project & API Initialization (2 Story Points)
*   **Description**: Prepare the Google Cloud project environment.
*   **Acceptance Criteria**:
    *   Create or select a GCP Project.
    *   Enable APIs: `run.googleapis.com`, `secretmanager.googleapis.com`, `artifactregistry.googleapis.com`.
    *   Create an Artifact Registry repository (Docker).

### Ticket 5.2: Secret Manager Migration (3 Story Points)
*   **Description**: Move all sensitive credentials from the local `.env` to the Cloud.
*   **Acceptance Criteria**:
    *   Upload `OPENAI_API_KEY`, `PINECONE_API_KEY`, and `JWT_SECRET` to Secret Manager.
    *   Grant the default Cloud Run service account `Secret Manager Secret Accessor` permissions.

### Ticket 5.3: Production Image Build & Registry Push (3 Story Points)
*   **Description**: Build the Docker image using the production `Dockerfile` and push to GCP.
*   **Acceptance Criteria**:
    *   Image built using `gcloud builds submit` or local `docker push`.
    *   Verification that the image size is optimized (using `python:3.12-slim`).
    *   Zero `.env` or temporary files included in the image.

### Ticket 5.4: Cloud Run Service Provisioning (5 Story Points)
*   **Description**: Deploy the microservice to Google Cloud Run.
*   **Acceptance Criteria**:
    *   Service deployed to `us-central1`.
    *   Secrets mounted as Environment Variables (e.g., `OPENAI_API_KEY` maps to the Secret Manager version).
    *   Resource limits set (e.g., 512MiB RAM, 1 CPU).
    *   Concurrency and scaling limits configured (Max 10 instances for pilot).

### Ticket 5.5: Post-Deployment Smoke Testing & Verification (3 Story Points)
*   **Description**: Final validation of the live endpoint.
*   **Acceptance Criteria**:
    *   Execute `pytest tests/test_integration.py` against the Cloud Run URL (overriding the base URL).
    *   Confirm 200 OK responses for valid TRL queries.
    *   Verify the "Polite Error Engine" handles unauthorized requests correctly in production.

---

## 🛠️ Resource Mapping
*   **Primary Tooling**: Google Cloud CLI (`gcloud`), Docker.
*   **Hosting**: Google Cloud Run (Serverless).
*   **Secrets**: Google Secret Manager.
*   **Documentation Output**: `SI/07_Product_Release/Deployment_Audit_Report.md`.

---
**Plan Approved for Execution.**
