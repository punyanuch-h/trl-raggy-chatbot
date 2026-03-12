# Sprint 2 Plan: Ingestion Engine & Vector Database (Final)

## Sprint Details
*   **Sprint Goal**: Build the data pipeline that parses TRL PDFs from local folders, generates embeddings, tags them with Privacy logic, and stores them in Pinecone.
*   **Duration**: 2 Weeks
*   **Methodology**: Agile & Test-Driven Development (TDD)
*   **Standard**: ISO/IEC 29110 Basic Profile

## Definition of Done (DoD)
A ticket in this sprint is considered "Done" when:
1.  **Code is Complete**: Implementation satisfies all Acceptance Criteria.
2.  **TDD Confirmed**: Pass rate 100% via `pytest` for all ingestion logic (mocked where needed to avoid live API cost).
3.  **Logs Retained**: The `pytest` execution report is saved in `SI/05_Test_Reports/`.
4.  **Documentation Synced**: The Vector Space design is mapped in `SI/02_Software_Design/Architecture_Design.md`.

---

## Sprint Backlog

### Ticket 2.1: Dependencies & Pinecone Index Initialization (3 Story Points)
*   **Description**: Update `requirements.txt` with all Sprint 2 libraries. Create a secure utility to connect to Pinecone via `PINECONE_API_KEY` and ensure a serverless index configured strictly for **1536 dimensions** exists.
*   **New Dependencies**: `pypdf`, `langchain-pinecone`, `langchain-openai`, `langchain-community`, `python-dotenv`
*   **Acceptance Criteria (TDD)**:
    *   **RED/GREEN**: Write a test using a mocked Pinecone client proving the initialization function handles both "index already exists" and "index must be created" states without crashing.

### Ticket 2.2: PDF Parsing Utility (3 Story Points)
*   **Description**: Build a LangChain document loader (`PyPDFLoader`) that scans `source/` and `source/private/` directories and extracts raw text from all PDF files.
*   **Acceptance Criteria (TDD)**:
    *   **RED/GREEN**: Write tests using a sample test PDF verifying text extraction succeeds. Ensure complex multi-page documents do not crash the loader.

### Ticket 2.3: Text Chunking and Embeddings (3 Story Points)
*   **Description**: Implement `RecursiveCharacterTextSplitter` and connect extracted text chunks to the `OpenAIEmbeddings` API (`text-embedding-3-small`, 1536 dimensions).
*   **Acceptance Criteria (TDD)**:
    *   **RED/GREEN**: Mock the OpenAI embeddings API call. Write tests confirming that no chunk exceeds the configured token limit and that the mocked embedding returns a list of exactly 1536 floats.

### Ticket 2.4: RBAC Metadata Injection & Upload (5 Story Points)
*   **Description**: Implement the privacy tagging logic. If a PDF path contains `source/private/`, the pipeline must append `{"role": "admin"}` to the vector's metadata before uploading to Pinecone. Public documents must carry NO role restriction tag.
*   **Acceptance Criteria (TDD)**:
    *   **RED/GREEN**: Unit tests independently verifying that private documents receive the restricted metadata tag and public documents explicitly do not.

### Ticket 2.5: Admin Re-Indexing Utility (3 Story Points)
*   **Description**: Satisfy `FR-05` (Business Requirements). Create an internal CLI script (e.g., `reindex.py`) that an Admin can execute locally to wipe and fully rebuild the Pinecone index from the current state of `source/` and `source/private/`. This is the mechanism by which new PDFs are registered into the system.
*   **Acceptance Criteria (TDD)**:
    *   **RED/GREEN**: Test proving the re-index CLI correctly detects and processes newly added PDFs.

---

## Resource Mapping
*   **Total Sprint Effort**: 17 Story Points
*   **Documentation**: `SI/01_Requirements_Specification/03_Technical_Requirements.md`
*   **Source Code**: Project root (e.g., `ingest.py`, `reindex.py`)
*   **Test Logs**: Automated to `SI/05_Test_Reports/`
