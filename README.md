# Raggy Bot: Technology Readiness Level (TRL) Expert

Raggy Bot is a professional, high-security Retrieval-Augmented Generation (RAG) API built following **ISO/IEC 29110** standards. It provides context-aware answers regarding TRL levels for the healthcare and education sectors.

## 🚀 Key Features
- **Semantic Search**: Powered by OpenAI `text-embedding-3-small` and Pinecone.
- **Role-Based Access Control (RBAC)**: Automatic data filtering based on JWT roles (`admin` vs. `researcher`).
- **Polite AI Persona**: Optimized for professional healthcare environments.
- **Cloud Ready**: Fully containerized for Google Cloud Run with Secret Manager support.

---

## 🛠️ Step 1: Local Setup

### 1. Clone & Initialize
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file in the root directory:
```bash
# Security
JWT_SECRET=your_secure_random_string

# AI Engines
OPENAI_API_KEY=sk-your-openai-key
PINECONE_API_KEY=your-pinecone-key
PINECONE_INDEX_NAME=trl-raggy-chatbot
```

---

## 📂 Step 2: Knowledge Ingestion
Raggy Bot learns from PDFs placed in the `source/` folder.
- **Public Docs**: Place in `source/`
- **Private Docs**: Place in `source/private/` (Only admins can access these).

Run the re-indexing utility to upload to Pinecone:
```bash
python reindex.py
```

---

## ⚡ Step 3: Running & Testing

### 1. Launch the API
```bash
python main.py
```
*The API will be available at `http://localhost:8080` (or `8001` if specified in code).*

### 2. Run Automated Tests (TDD)
We maintain a strict 100% pass rate.
```bash
# Using the custom ISO test script
.\run_tests.bat
```

### 3. Interactive Documentation
Visit `http://localhost:8080/docs` to view the interactive Swagger UI and test endpoint calls.

---

## ☁️ Step 4: Production Deployment
To deploy to **Google Cloud Run**, refer to:
- `PM/GCP_Secret_Setup.md`: To upload keys to Secret Manager.
- `PM/deploy_instructions.md`: For the final `gcloud` deployment command.

---

## 📄 Documentation Index
- **User Manual**: `SI/06_User_Manual/User_Manual.md`
- **Architecture**: `SI/02_Software_Design/Architecture_Design.md`
- **Project Journey**: `SI/07_Product_Release/Development_Journey_Summary.md`

---
**Status**: v1.0 Release Candidate
**Standard**: ISO/IEC 29110 Basic Profile
