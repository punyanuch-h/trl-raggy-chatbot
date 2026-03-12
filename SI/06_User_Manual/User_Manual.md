# Raggy Bot: User Manual (TRL Expert)

## 1. Introduction
Welcome to **Raggy Bot**, your professional AI assistant specializing in Technology Readiness Levels (TRL) for the healthcare and education sectors. Raggy Bot uses Retrieval-Augmented Generation (RAG) to provide accurate, context-aware answers based on official documentation.

## 2. Getting Started
### Prerequisites
- An active JWT (JSON Web Token) with a `role` claim (`admin` or `researcher`).
- The API endpoint URL (provided after deployment).

## 3. Using the API
### The `/raggy/trl` Endpoint
Send a `POST` request to the following endpoint:
`POST /raggy/trl`

**Request Headers:**
- `Content-Type: application/json`
- `Authorization: Bearer <your_jwt_token>`

**Request Body:**
```json
{
  "query": "What are the characteristics of TRL 4 in a laboratory environment?"
}
```

## 4. Understanding Roles & Access
Raggy Bot enforces **Role-Based Access Control (RBAC)** at the database level:
- **Admin**: Has full access to all documentation, including private research in the `source/private` folder.
- **Researcher**: Has access only to public/general TRL documentation. Any private data is automatically filtered out.

## 5. Tone and Constraints
- **Tone**: The bot is designed to be empathetic, polite, and professional.
- **Accuracy**: The bot will *only* answer based on the provided PDF documentation.
- **Safety**: If the bot does not know the answer, it will politely decline to guess. If you ask a question unrelated to TRL, it will ask you to stay on topic.

## 6. Troubleshooting
- **"I apologize, but I couldn't verify your access"**: Your JWT token is either missing, expired, or invalid.
- **"I encountered a technical difficulty"**: The API is having trouble connecting to the database or AI engine. Wait a few moments and try again.
