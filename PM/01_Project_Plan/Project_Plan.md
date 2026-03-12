# Project Plan: Raggy Bot

## 1. Project Overview
* **Project Name**: Raggy Bot
* **Project Framework**: Agile (2-week Sprints) combined with Test-Driven Development (TDD)
* **Standard Operating Procedure**: ISO/IEC 29110 Basic Profile

## 2. Business Requirements
These requirements dictate the scope and direction of the first upcoming sprint planning and system design:

1. **System Purpose**: This project is a Retrieval-Augmented Generation (RAG) application designed to accurately answer questions regarding **Technology Readiness Levels (TRL)**.
2. **User Roles**: The application is tailored for two distinct roles:
   * **Researcher**: Queries the bot to understand TRL levels.
   * **Admin**: Manages the bot and potentially updates the standard procedures.
3. **Deliverable**: The final output of this RAG project will be a fully functional **API endpoint**. This API acts as an interface allowing external services to integrate seamlessly and call Raggy Bot for query results.
4. **Data Sources**: Raggy Bot will ingest and parse **PDF files** exclusively stored in the root `source/` folder to formulate accurate TRL responses.

## 3. Sprint Cadence (Agile)
* **Duration**: 2 weeks per Sprint.
* **Testing Policy**: Red-Green-Refactor sequence is strictly enforced per sprint user story execution.

## 4. Key Metrics for Evaluation
* **Time Reduction**: The primary success metric is significantly reducing the time it takes for a researcher to understand what a specific TRL is and discovering exactly how their research project can achieve that TRL level.
