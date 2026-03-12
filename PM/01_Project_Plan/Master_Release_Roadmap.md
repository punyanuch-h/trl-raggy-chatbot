# Raggy Bot: Master Release Roadmap

## Overview
This roadmap outlines all remaining Agile Sprints required to fulfill the Version 3 Business and Technical Requirements and achieve a production-ready, ISO 29110 compliant release deployed on **Google Cloud Run**.

## Sprint 1: Security & API Foundation [COMPLETED]
*   **Goal**: Establish the core architecture, testing framework, Exception Engine, and JWT secure API skeleton.
*   **Status**: Done (100% Test Coverage).

---

## Sprint 2: The Ingestion Engine & Vector Database
*   **Sprint Goal**: Build the data pipeline that parses TRL PDFs from local folders, generates embeddings, tags them with Privacy logic, and stores them in Pinecone.
*   **Duration**: 2 Weeks.
*   **Backlog**:
    *   **Ticket 2.1: Pinecone Index Initialization**: Programmatically connect to the Pinecone cloud environment and ensure the index is configured strictly for **1536 dimensions** (to match OpenAI).
    *   **Ticket 2.2: PDF Parsing Utility (TDD)**: Build a LangChain document loader that accurately reads and extracts raw text from PDFs inside the root `source/` folder.
    *   **Ticket 2.3: Chunking & Embeddings (TDD)**: Implement the LangChain Text Splitter and connect the extracted text chunks to the `OpenAIEmbeddings` (specifically `text-embedding-3-small` model) API.
    *   **Ticket 2.4: RBAC Metadata Injection**: Create the logic that detects if a PDF exists in `source/private`. If it does, automatically attach the `{"role": "admin"}` metadata tag to its Pinecone vectors before upload.

---

## Sprint 3: The Generation Engine & Prompt Engineering
*   **Sprint Goal**: Connect the RAG logic to the API endpoint, build the healthcare/education-focused prompt, and enforce role-based vector retrieval.
*   **Duration**: 2 Weeks.
*   **Backlog**:
    *   **Ticket 3.1: Strict Role-Based Vector Retrieval (TDD)**: Build the LangChain retriever logic. If the API user is a `researcher`, enforce a strict Pinecone metadata filter that permanently excludes the `role: admin` tag from the search space.
    *   **Ticket 3.2: System Prompt Engineering**: Draft the strict LangChain Chat Prompt Template constraining OpenAI to an exceedingly polite, empathetic, and professional tone suitable for the Healthcare/Education sector.
    *   **Ticket 3.3: LLM Endpoint Integration (TDD)**: Connect the completed retrieval chain and OpenAI `gpt-4o-mini` language model into the existing FastAPI `/raggy/trl` route.
    *   **Ticket 3.4: Evaluation via RAG Metrics**: Implement non-deterministic testing (e.g., Ragas or custom evaluator scripts) to test the final generated responses for Faithfulness and Politeness before release.

---

## Sprint 4: Google Cloud Run Deployment
*   **Sprint Goal**: Containerize the microservice, securely manage the JWT/OpenAI/Pinecone secrets, and deploy the system to the internet via Google Cloud Run.
*   **Duration**: 1 Week.
*   **Backlog**:
    *   **Ticket 4.1: Docker Containerization**: Write the `Dockerfile` and `.dockerignore` optimized specifically for FastAPI and ASGI Python execution. Ensure zero local paths (like `SI/05_Test_Reports/`) are baked into the container.
    *   **Ticket 4.2: Secret Management Strategy**: Define and document the protocol for migrating local `.env` values (`JWT_SECRET`, `OPENAI_API_KEY`, `PINECONE_API_KEY`) into Google Cloud Secret Manager.
    *   **Ticket 4.3: Google Cloud Run Provisioning**: Document and execute the exact Google Cloud Shell deployment commands (`gcloud run deploy`), ensuring scaling limits align with the 100-user free-tier infrastructure requirement.
    *   **Ticket 4.4: ISO 29110 Release Audit**: Perform the final compliance check. Ensure all test scripts passed, architecture docs are finalized, and compile the final software package directly into `SI/07_Product_Release/`.

---
*Roadmap Approved. Current Active Cycle: SPRINT 2*
