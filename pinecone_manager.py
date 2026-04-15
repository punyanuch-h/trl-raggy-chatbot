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

    def get_connection_report(self):
        """
        Return a safe diagnostic snapshot proving the app can reach Pinecone
        and inspect the configured vector index.
        """
        index_info = self.client.describe_index(self.index_name)
        index = self.get_index()
        stats = index.describe_index_stats()

        namespaces = {}
        if isinstance(stats, dict):
            raw_namespaces = stats.get("namespaces", {}) or {}
        else:
            raw_namespaces = getattr(stats, "namespaces", {}) or {}
        for namespace, details in raw_namespaces.items():
            vector_count = getattr(details, "vector_count", None)
            if vector_count is None and isinstance(details, dict):
                vector_count = details.get("vector_count", 0)
            namespaces[namespace or "default"] = int(vector_count or 0)

        total_vector_count = getattr(stats, "total_vector_count", None)
        if total_vector_count is None and isinstance(stats, dict):
            total_vector_count = stats.get("total_vector_count", 0)

        dimension = getattr(index_info, "dimension", None)
        if dimension is None and isinstance(index_info, dict):
            dimension = index_info.get("dimension")

        metric = getattr(index_info, "metric", None)
        if metric is None and isinstance(index_info, dict):
            metric = index_info.get("metric")

        host = getattr(index_info, "host", None)
        if host is None and isinstance(index_info, dict):
            host = index_info.get("host")

        if isinstance(index_info, dict):
            status = index_info.get("status")
        else:
            status = getattr(index_info, "status", None)

        if isinstance(status, dict):
            ready = bool(status.get("ready", False))
            state = status.get("state")
        else:
            ready = bool(getattr(status, "ready", False))
            state = getattr(status, "state", None)

        return {
            "index_name": self.index_name,
            "host": host,
            "dimension": dimension,
            "metric": metric,
            "ready": ready,
            "state": state,
            "total_vector_count": int(total_vector_count or 0),
            "namespaces": namespaces,
        }
