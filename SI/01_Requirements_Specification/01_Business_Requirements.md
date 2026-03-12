# Business Requirements Specification: Raggy Bot

## 1. Executive Summary
**Raggy Bot** is a Retrieval-Augmented Generation (RAG) system specifically designed to answer queries regarding Technology Readiness Levels (TRL). The primary business goal is to significantly reduce the time researchers spend attempting to understand TRL criteria and how their projects align with those levels.

## 2. System Scope & Deliverables
*   **System Type**: Headless Microservice (API Backend).
*   **User Interface**: None. This project will not provide a frontend GUI.
*   **Deliverable**: A single, robust RESTful API endpoint that external services (such as an existing web frontend or mobile app) can call.
*   **Data Sources**: The system will serve answers by reading from PDF documents stored within a predefined file structure (`source/` and `source/private`).

## 3. User Roles & Privacy Control
The system business logic must behave differently depending on the role of the user passing the query:
1.  **Researcher**: 
    *   **Goal**: Queries the bot to understand TRL levels.
    *   **Access Restriction**: Answers generated for a researcher MUST NOT use any confidential information or documents stored inside the `source/private` directory.
2.  **Admin**:
    *   **Goal**: Manages the bot, procedures, and potentially asks high-level systematic questions.
    *   **Access Level**: Full. Answers generated for an admin may utilize all standard data in `source/` AND restricted data located in `source/private`.

## 4. Key Performance Indicators (KPIs)
*   **Primary Metric**: Time Reduction for researchers seeking TRL comprehension.
*   **Scalability**: Must support at least 100 concurrent/active internal users effectively on the chosen infrastructure free tier.
