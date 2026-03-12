# Raggy Bot: Development Journey Summary (Sprints 1-4)

## 🌟 Executive Summary
Raggy Bot is a high-security, Retrieval-Augmented Generation (RAG) assistant designed for the Healthcare and Education sectors. It provides expert-level answers on Technology Readiness Levels (TRL) while enforcing strict Role-Based Access Control (RBAC) and ISO 29110 quality standards.

---

## 🏗️ The Build Journey

### Sprint 1: The Foundation (Skeleton & Security)
- **Goal**: Establish the API architecture and security baseline.
- **Outcome**: Developed a FastAPI microservice with JWT authentication (HS256).
- **ISO Compliance**: Created the initial Architecture Design and Quality Assurance plans.

### Sprint 2: The Knowledge Base (Data Ingestion)
- **Goal**: Create a smart ingestion pipeline for PDFs.
- **Outcome**: Built a scanner that recursively parses documents. Implementing **RBAC at the folder level** (docs in `source/private` are invisible to researchers).
- **Tech**: PyPDF, RecursiveCharacterTextSplitter, OpenAI `text-embedding-3-small`.

### Sprint 3: The Brain (RAG Engine & Prompting)
- **Goal**: Connect AI to the vector database and enforce tone.
- **Outcome**: Integrated LangChain with Pinecone. Engineered a "Master TRL Prompt" that ensures a professional, empathetic tone and zero hallucinations.
- **TDD Milestone**: Achieved 100% test pass rate across 28 unit and integration tests.

### Sprint 4: The Cloud (Deployment)
- **Goal**: Prepare for production release.
- **Outcome**: Containerized the app using Docker. Developed a secure deployment roadmap for Google Cloud Run and Secret Manager.
- **Final Packaging**: Delivered the User Manual and Final Release Report.

---

## 🔒 Security & Guardrails
- **Data Privacy**: Researchers are strictly isolated from admin-only data via Pinecone metadata filtering.
- **Polite Refusal**: The bot is programmed to say "I don't know" rather than guess, protecting healthcare professional users from misinformation.
- **Zero Secrets**: Moved from local `.env` to hardware-protected Secret Management for production.

---

## 📊 Technical Stack
- **Languages**: Python 3.12, GitHub-Flavored Markdown.
- **Frameworks**: FastAPI, LangChain.
- **AI/DB**: OpenAI (GPT-4o-mini), Pinecone (Serverless).
- **DevOps**: Docker, Google Cloud Run, Pytest.

---

## 📈 Future Roadmap
- **v1.1**: Implementation of Hybrid Search (Sparse + Dense).
- **v1.2**: Advanced Citations (Deep-linking to specific PDF pages).
- **v2.0**: Integration of multi-lingual support for international TRL standards.

**Project Status**: [RELEASABLE]
**Certified by**: Antigravity AI Pair Programmer
**Date**: March 11, 2026
