# GCP Secret Manager Setup Guide: Raggy Bot

To move from local `.env` to Google Cloud production security, follow these steps to upload your secrets.

## 1. Enable Secret Manager API
Run this command to ensure the API is active in your project:
```bash
gcloud services enable secretmanager.googleapis.com
```

## 2. Create and Upload Secrets
Execute the following commands one by one. Replace the `[VALUES]` with your actual keys.

### A. OpenAI API Key
```bash
echo -n "[YOUR_OPENAI_API_KEY]" | gcloud secrets create OPENAI_API_KEY --data-file=-
```

### B. Pinecone API Key
```bash
echo -n "[YOUR_PINECONE_API_KEY]" | gcloud secrets create PINECONE_API_KEY --data-file=-
```

### C. Pinecone Index Name
```bash
echo -n "[YOUR_PINECONE_INDEX_NAME]" | gcloud secrets create PINECONE_INDEX_NAME --data-file=-
```

### D. JWT Secret (Production Key)
*Generate a random string (e.g., using `openssl rand -hex 32`)*
```bash
echo -n "[YOUR_SECURE_JWT_SECRET]" | gcloud secrets create JWT_SECRET --data-file=-
```

## 3. Grant Permissions to Cloud Run
Cloud Run needs permission to read these secrets. If you are using the default Compute Engine service account:

```bash
PROJECT_NUMBER=$(gcloud projects describe [GCP_PROJECT_ID] --format="value(projectNumber)")

gcloud projects add-iam-policy-binding [GCP_PROJECT_ID] \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

## 4. Verification
Once uploaded, the application will automatically see these as environment variables when we link them during the `gcloud run deploy` step in Ticket 4.3.
