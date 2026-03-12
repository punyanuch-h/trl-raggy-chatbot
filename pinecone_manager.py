import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

# Load secrets from .env file
load_dotenv()


class PineconeManager:
    """
    Manages Pinecone connection and index lifecycle for Raggy Bot.
    On initialization, it connects to the Pinecone cloud client and 
    ensures the required index (1536 dims, cosine metric) exists.
    """

    def __init__(self):
        self.api_key = os.environ.get("PINECONE_API_KEY")
        self.index_name = os.environ.get("PINECONE_INDEX_NAME", "raggy-bot-trl")

        # Connect to Pinecone cloud client
        self.client = Pinecone(api_key=self.api_key)

        # Ensure index exists, create if missing
        self._ensure_index()

    def _ensure_index(self):
        """
        Checks if the configured index exists.
        If it doesn't exist, it creates one with 1536 dimensions
        using cosine similarity, which matches the OpenAI embedding model.
        """
        existing_indexes = self.client.list_indexes().names()

        if self.index_name not in existing_indexes:
            print(f"[PineconeManager] Index '{self.index_name}' not found. Creating...")
            self.client.create_index(
                name=self.index_name,
                dimension=1536,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            print(f"[PineconeManager] Index '{self.index_name}' created successfully.")
        else:
            print(f"[PineconeManager] Index '{self.index_name}' already exists. Skipping creation.")

    def get_index(self):
        """Returns the active Pinecone index object for upserting or querying."""
        return self.client.Index(self.index_name)
