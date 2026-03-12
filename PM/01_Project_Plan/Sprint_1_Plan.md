# Sprint 1 Plan: Raggy Bot Foundation

## Sprint Details
*   **Sprint Goal**: Establish the core architecture, testing framework, and secure API skeleton for Raggy Bot.
*   **Duration**: 2 Weeks
*   **Methodology**: Agile & Test-Driven Development (TDD)
*   **Standard**: ISO/IEC 29110 Basic Profile

## Definition of Done (DoD)
A ticket in this sprint is strictly considered "Done" only when:
1.  **Code is Complete**: Implementation satisfies all Acceptance Criteria.
2.  **TDD Confirmed**: Test coverage passes 100% for the new feature (`pytest`).
3.  **Logs Retained**: The `pytest` execution report is successfully exported and saved into the `SI/05_Test_Reports/` directory.
4.  **Documentation Synced**: Architectural or API changes are updated in `SI/02_Software_Design/`.

## Sprint Backlog
The following User Stories and Technical Tasks are selected for Sprint 1:

### Ticket 1: Project Initialization & Test Automation (1 Story Point)
*   **Description**: Create the Python virtual environment, install dependencies (`fastapi`, `uvicorn`, `pytest`, `langchain`, `pinecone-client`, `openai`, `PyJWT`), and write the automated test-logging script.
*   **Acceptance Criteria**: 
    *   Virtual environment is functional.
    *   `requirements.txt` is created and locked.
    *   **Test Automation**: A local script (e.g., `run_tests.bat` or `.sh`) is created to automatically run `pytest` and output the results directly into `SI/05_Test_Reports/test_log.txt`.
*   **Artifacts**: `PM/03_Project_Repository`, `SI/05_Test_Reports`

### Ticket 2: The Core API Skeleton & Software Design (3 Story Points)
*   **Description**: Build the primary FastAPI web server bound to Port `8001` with CORS whitelisting for `http://localhost:3000`. Export the API specification.
*   **Acceptance Criteria (TDD)**:
    *   **RED**: Write a failing `pytest` against `/raggy/trl` expecting a 200 OK.
    *   **GREEN**: Implement the `main.py` FastAPI logic to make the test pass.
    *   **Software Design**: FastAPI's generated `openapi.json` must be saved to `SI/02_Software_Design/` as the formal API Architectural Document.
*   **Artifacts**: `SI/04_Test_Cases`, `SI/03_Source_Code`, `SI/02_Software_Design`

### Ticket 3: Exception Engine & Polite Error Handling (3 Story Points)
*   **Description**: Implement custom FastAPI exception handlers to ensure technical 422/500 errors are suppressed and replaced with polite text-based conversational apologies (following Healthcare & Education regulations).
*   **Acceptance Criteria (TDD)**:
    *   **RED**: Write a failing test sending invalid data to the endpoint and expecting a polite text response.
    *   **GREEN**: Implement the FastAPI Exception Handler.
*   **Artifacts**: `SI/04_Test_Cases_and_Procedures`, `SI/03_Source_Code`

### Ticket 4: JWT Authentication Middleware (5 Story Points)
*   **Description**: Implement the security layer extracting the JWT from `Authorization: Bearer`, decoding it securely via the `.env` secret, and mapping the user role (`admin` or `researcher`).
*   **Acceptance Criteria (TDD)**:
    *   **RED**: Write tests simulating valid tokens, invalid tokens, and missing tokens, expecting correct authorization or polite fallback responses.
    *   **GREEN**: Implement the `jwt` decoding logic and privacy downgrade mechanisms.
*   **Artifacts**: `SI/04_Test_Cases`, `SI/03_Source_Code`

---
## Resource Mapping
*   **Total Sprint Effort**: 12 Story Points
*   **Documentation**: `SI/01_Requirements_Specification/03_Business_Requirements.md` & `03_Technical_Requirements.md`
*   **Test Logs**: Automated to `SI/05_Test_Reports/`
*   **Software Design**: API Specifications to `SI/02_Software_Design/`
*   **Release**: The Sprint output will be packaged in `SI/07_Product_Release/`

---
*Status: READY FOR EXECUTION*
