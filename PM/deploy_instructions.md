# Google Cloud Deployment Guide: Ticket 4.3

Follow these steps to deploy Raggy Bot to the public internet using Google Cloud Run. 

## 1. Local Prerequisites
Ensure you have the Google Cloud SDK installed and are logged in:
```powershell
gcloud auth login
gcloud config set project [GCP_PROJECT_ID]
```

## 2. Enable Billing & APIs
Ensure your project has billing enabled and the necessary APIs active:
```powershell
gcloud services enable artifactregistry.googleapis.com run.googleapis.com cloudbuild.googleapis.com
```

## 3. The Big Deploy Command
Run this command from your project root. This will:
1.  **Build** the Docker image in the cloud (using Cloud Build).
2.  **Push** it to a temporary registry.
3.  **Deploy** to Cloud Run.
4.  **Map** your Secrets from Secret Manager to the container.

```powershell
gcloud run deploy raggy-bot-api `
  --source . `
  --region us-east-1 `
  --platform managed `
  --set-secrets="OPENAI_API_KEY=OPENAI_API_KEY:latest,PINECONE_API_KEY=PINECONE_API_KEY:latest,PINECONE_INDEX_NAME=PINECONE_INDEX_NAME:latest,JWT_SECRET=JWT_SECRET:latest" `
  --allow-unauthenticated
```

## 4. Post-Deployment Verification
Once finalized, the command will output a **Service URL** (e.g., `https://raggy-bot-trl-xyz.a.run.app`). 

Test it using `curl` or Postman:
```bash
# Verify the API is alive
GET https://[YOUR_URL]/docs
```

---
**⚠️ Important Security Reminders:**
- **Secret Names**: Ensure the names in your Secret Manager match exactly with the `--set-secrets` flags above.
- **Port**: Cloud Run automatically detects port `8080` from our Dockerfile.
- **IAM**: If you get a "Permission Denied" error on secrets, revisit the `roles/secretmanager.secretAccessor` command in your Setup guide.
