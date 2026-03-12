# Business Requirements Specification: Raggy Bot (Version 3)

## 1. Executive Summary
**Raggy Bot** is a Retrieval-Augmented Generation (RAG) system specifically designed to answer queries regarding Technology Readiness Levels (TRL). The system operates within the **healthcare and education sectors**, which strictly require all system interactions and AI-generated outputs to maintain an exceedingly polite, professional, and empathetic tone. 

The primary business goal remains to significantly reduce the time researchers spend attempting to understand TRL criteria and how their projects align with those levels.

## 2. System Scope & Deliverables
*   **System Type**: Headless Microservice (API Backend).
*   **User Interface**: None. This project will not provide a frontend GUI. The Frontend client will call this service directly.
*   **Deliverable**: A single RESTful API endpoint that the Frontend client application will query.
*   **Data Sources**: The system will serve answers by reading from PDF documents stored within a predefined file structure (`source/` and `source/private`).
*   **Interaction Model**: The system operates as a single-turn (single-shot) Q&A system. Each query is treated independently without retaining conversational memory across requests.

## 3. User Roles, Privacy & Authentication
The system business logic must behave differently depending on the role of the user passing the query:
1.  **Authentication Control**: The Frontend client will send a JWT (JSON Web Token) directly to Raggy Bot to authenticate the session and determine the user's role.
2.  **Researcher**: 
    *   **Goal**: Queries the bot to understand TRL levels.
    *   **Access Restriction**: Answers generated for a researcher MUST NOT use any confidential information or documents stored inside the `source/private` directory.
3.  **Admin**:
    *   **Goal**: Manages the bot, procedures, and potentially asks high-level systematic questions.
    *   **Access Level**: Full. Answers generated for an admin may utilize all standard data in `source/` AND restricted data located in `source/private`.

## 4. Input Constraints & Polite Error Handling
*   **Input Acceptance**: The Raggy Bot system is exclusively designed to process **text-based queries**.
*   **Polite Payload Responses**: Software errors, invalid file uploads from a user, missing fields, or system timeouts **must not throw standard technical error codes (like HTTP 422 or 500) to the user**. 
    *   Instead, the system must intercept the error, stop the crash, and return a polite, conversational text response (e.g., *"I'm sorry, I am currently experiencing an issue processing that. Could you please try asking your question again as plain text?"*).
*   **Polite, Strict Security Responses**: Security-related errors (e.g., missing JWT token, expired signature, failed verification) must also return a soft, polite response that explicitly **avoids leaking any sensitive data or system architecture details**. 
    *   The bot will simply respond: *"I apologize, but I am having trouble verifying your access session. For your protection, could you please log in again?"*

## 5. Key Performance Indicators (KPIs)
*   **Primary Metric**: Time Reduction for researchers seeking TRL comprehension.
*   **Tone Compliance**: 100% adherence to the polite communication standards required by the healthcare and education industries.
*   **Scalability**: Must support at least 100 concurrent/active internal users effectively on the chosen infrastructure free tier.
