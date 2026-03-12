# Business Requirements Specification: Raggy Bot (Version 2)

## 1. Executive Summary
**Raggy Bot** is a Retrieval-Augmented Generation (RAG) system specifically designed to answer queries regarding Technology Readiness Levels (TRL). The system operates within the **healthcare and education sectors**, which strictly require all system interactions and AI-generated outputs to maintain an exceedingly polite, professional, and empathetic tone. 

The primary business goal remains to significantly reduce the time researchers spend attempting to understand TRL criteria and how their projects align with those levels.

## 2. System Scope & Deliverables
*   **System Type**: Headless Microservice (API Backend).
*   **User Interface**: None. This project will not provide a frontend GUI. The Frontend client will call this service directly.
*   **Deliverable**: A single RESTful API endpoint that the Frontend client application will query.
*   **Data Sources**: The system will serve answers by reading from PDF documents stored within a predefined file structure (`source/` and `source/private`).

## 3. User Roles, Privacy & Authentication
The system business logic must behave differently depending on the role of the user passing the query:
1.  **Authentication Control**: The Frontend client will send a JWT (JSON Web Token) directly to Raggy Bot to authenticate the session and determine the user's role.
2.  **Researcher**: 
    *   **Goal**: Queries the bot to understand TRL levels.
    *   **Access Restriction**: Answers generated for a researcher MUST NOT use any confidential information or documents stored inside the `source/private` directory.
3.  **Admin**:
    *   **Goal**: Manages the bot, procedures, and potentially asks high-level systematic questions.
    *   **Access Level**: Full. Answers generated for an admin may utilize all standard data in `source/` AND restricted data located in `source/private`.

## 4. Input Constraints & Error Handling
*   **Input Acceptance**: The Raggy Bot system is exclusively designed to process **text-based queries**.
*   **Graceful Handling**: If a user attempts to upload or send an image, document, or non-text file as their query, the system **must not crash or return a technical system error** (like HTTP 400 or 500). Instead, the bot must intercept the mismatch and return a polite, conversational response apologizing and explaining that it can currently only read and process text.

## 5. Key Performance Indicators (KPIs)
*   **Primary Metric**: Time Reduction for researchers seeking TRL comprehension.
*   **Tone Compliance**: 100% adherence to the polite communication standards required by the healthcare and education industries.
*   **Scalability**: Must support at least 100 concurrent/active internal users effectively on the chosen infrastructure free tier.
