import os
import uuid
from typing import List
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

load_dotenv()


class VectorUploader:
    """
    Handles embedding generation and vector upsert into Pinecone for Raggy Bot.

    RBAC Enforcement:
    - Chunks tagged with access='private' receive role='admin' in Pinecone metadata.
    - Chunks tagged with access='public' do NOT receive any role restriction tag.
    This ensures LangChain's retriever can filter out private vectors for researcher queries.

    Performance:
    - All vectors are uploaded in a single batch upsert call for efficiency.
    """

    def __init__(self, pinecone_manager):
        self.pinecone_manager = pinecone_manager
        base_url = os.environ.get("OPENAI_BASE_URL")
        print(f"[DEBUG] VectorUploader using base_url: {base_url}")
        self.embedder = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
            base_url=base_url
        )

    def upload(self, chunks: List[Document]) -> None:
        """
        Embeds a list of Document chunks and upserts them into Pinecone
        in a single batch call with correct RBAC metadata tags.

        Args:
            chunks: List of LangChain Document objects from TextChunker.split().
        """
        if not chunks:
            return

        # Extract text content for embedding
        texts = [chunk.page_content for chunk in chunks]

        # Generate embeddings via OpenAI text-embedding-3-small
        embeddings = self.embedder.embed_documents(texts)

        # Build Pinecone vector dicts with RBAC metadata injection
        vectors = []
        for chunk, embedding in zip(chunks, embeddings):
            metadata = dict(chunk.metadata)
            metadata["text"] = chunk.page_content

            # RBAC: only private chunks get the admin role restriction tag
            if metadata.get("access") == "private":
                metadata["role"] = "admin"

            vectors.append({
                "id": str(uuid.uuid4()),
                "values": embedding,
                "metadata": metadata
            })

        # Single batch upsert into Pinecone index for performance
        index = self.pinecone_manager.get_index()
        index.upsert(vectors=vectors)

        print(f"[VectorUploader] Successfully upserted {len(vectors)} vectors into Pinecone.")
