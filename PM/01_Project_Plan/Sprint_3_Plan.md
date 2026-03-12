# Sprint 3 Plan: Generation Engine & Prompt Engineering (Final)

## Sprint Details
*   **Sprint Goal**: Connect the RAG logic to the API endpoint, build the healthcare/education-focused prompt, enforce role-based vector retrieval, and validate out-of-context query handling.
*   **Duration**: 2 Weeks
*   **Methodology**: Agile & TDD
*   **Standard**: ISO/IEC 29110 Basic Profile

## Definition of Done (DoD)
A ticket in this sprint is considered "Done" when:
1.  **Code is Complete**: Implementation satisfies all Acceptance Criteria.
2.  **TDD Confirmed**: Pass rate 100% via `pytest`. All OpenAI calls must be **mocked** via `unittest.mock` in unit tests. Live API calls are reserved only for manual smoke testing.
3.  **Logs Retained**: The `pytest` execution report is saved in `SI/05_Test_Reports/`.
4.  **Documentation Synced**: `Architecture_Design.md` updated with the final RAG chain structure.

---

## Sprint Backlog

### Ticket 3.1: Strict Role-Based Vector Retrieval (5 Story Points)
*   **Description**: Build a LangChain retriever connecting to Pinecone. If the API user JWT decodes to `researcher`, inject a strict metadata filter into the Pinecone query explicitly excluding `{ "role": {"$eq": "admin"} }`. Admin users receive the unfiltered full context.
*   **Acceptance Criteria (TDD)**:
    *   **RED/GREEN**: Write tests using a mocked Pinecone retriever verifying that a `researcher` query does NOT return any chunks tagged with `role: admin`, and that an `admin` query returns full results.

### Ticket 3.2: System Prompt Engineering & Guardrails (3 Story Points)
*   **Description**: Draft the strict LangChain `ChatPromptTemplate` that:
    *   Instructs `gpt-4o-mini` to **only answer from the provided context chunks** and politely decline any question that is entirely outside of TRL subject matter.
    *   Enforces an **exceedingly polite, empathetic, and professional tone** required by Healthcare & Education regulations.
    *   If the context chunks contain no relevant information, the bot must NOT hallucinate but instead respond: *"I'm sorry, I don't have enough information to answer that specific question. Could you try rephrasing it or asking something related to TRL levels?"*
*   **Acceptance Criteria (TDD)**:
    *   **RED/GREEN**: Simulate a mocked LLM response. Write tests asserting the prompt template correctly structures the `system`, `context`, and `user` blocks. Write an additional test verifying that an off-topic query (mocked) returns the polite redirect response.

### Ticket 3.3: LLM Endpoint Integration with Mock Strategy (5 Story Points)
*   **Description**: Connect the completed Prompt Template and Retriever logic into the FastAPI `/raggy/trl` route (`main.py`). The endpoint must now return real context-driven answers and source citations instead of mock payloads.
*   **Mocking Strategy for TDD**: Use `unittest.mock.patch` to replace OpenAI and Pinecone clients with deterministic local stubs during unit tests, preventing flakiness and avoiding live API costs.
*   **Acceptance Criteria (TDD)**:
    *   **RED/GREEN**: Integration tests (mocked) proving real API `QueryRequest` payloads produce `QueryResponse` objects with a populated `answer` and `sources` list.

### Ticket 3.4: RAG Metric Evaluation Strategy (3 Story Points)
*   **Description**: Implement non-deterministic evaluators (e.g., Ragas or custom assertion scripts) to assess:
    *   **Faithfulness**: Answers stay grounded in the source context (low hallucination rate).
    *   **Answer Relevance**: Response pertains to the TRL question asked.
    *   **Politeness Compliance**: Verifies responses contain no inappropriate or unprofessional language.
*   **Acceptance Criteria**:
    *   Evaluation scripts are ready and saved. A baseline evaluation score threshold is defined before any sprint merge.

---

## Resource Mapping
*   **Total Sprint Effort**: 16 Story Points
*   **Documentation**: Updates to `SI/02_Software_Design/Architecture_Design.md`
*   **Source Code**: Project root (`rag_chain.py`, `prompts.py`)
*   **Test Logs**: Automated to `SI/05_Test_Reports/`
