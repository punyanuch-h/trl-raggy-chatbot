# Raggy Bot: User Manual (TRL Expert)

## 1. Introduction
Raggy Bot is a professional AI assistant for Technology Readiness Level (TRL) questions in healthcare and education contexts. It uses Retrieval-Augmented Generation (RAG) so answers stay grounded in project documents.

## 2. Getting Started
### Prerequisites
- A valid JWT with a `role` claim of `admin` or `researcher`
- The deployed API URL, or `http://127.0.0.1:8080` for local use

## 3. Using the API
### Endpoint
`POST /raggy/trl`

### Request headers
- `Content-Type: application/json`
- `Authorization: Bearer <your_jwt_token>`
- Optional: `X-Request-ID: <client_correlation_id>`
- Optional: `X-Session-ID: <session_group_id>`

### Request body
```json
{
  "query": "What are the characteristics of TRL 4 in a laboratory environment?"
}
```

### Response body
```json
{
  "answer_markdown": "## TRL Response\n\nTRL 4 focuses on component validation in a laboratory environment."
}
```

## 4. Understanding the Markdown Output
- `answer_markdown` is the only response field returned by the endpoint.
- It is the canonical presentation format for clients and should be rendered as markdown.
- The backend constrains output to safe markdown patterns: one level-2 heading, short paragraphs, and simple hyphen bullets.
- Raw HTML, tables, code fences, and deep heading hierarchies are intentionally out of scope.

## 5. Understanding Roles & Access
Raggy Bot enforces Role-Based Access Control (RBAC):
- `admin` can access public and private TRL documents, including content from `source/private/`
- `researcher` can access only public/general TRL documents

## 6. Tone and Constraints
- The bot uses a polite, professional, and supportive tone
- The bot answers only from the indexed PDF documentation
- If the context is insufficient, the bot declines to guess
- If the question is off-topic, the bot redirects the user back to TRL-related questions

## 7. Troubleshooting
- If the response asks you to log in again, the JWT is missing, invalid, or expired
- If the response mentions a technical difficulty, the API could not complete retrieval or LLM processing
- If the response format looks unexpected, check the current OpenAPI contract in `SI/02_Software_Design/openapi.json`

## 8. Metadata Audit Review
Sprint 7 stores metadata only for monitoring and audit support. It does not store conversation transcript content.

Stored metadata fields:
- `request_id`
- `session_id`
- `user_id`
- `role`
- `timestamp`
- `response_status`
- `route_path`
- `model_name`

Excluded fields:
- `query`
- `answer`
- `answer_markdown`
- retrieved context

Admin-only internal verification endpoints:
- `GET /internal/metadata/requests?limit=20`
- `GET /internal/metadata/sessions/{session_id}`
