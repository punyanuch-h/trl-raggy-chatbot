import os
from typing import List
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

load_dotenv()


class TextChunker:
    """
    Handles splitting of LangChain Document objects into smaller
    chunks suitable for vector database ingestion.

    Configuration:
    - chunk_size:    1000 characters per chunk (fits within OpenAI token limits)
    - chunk_overlap: 150 characters overlap to preserve context across boundaries

    All original metadata is preserved on every chunk.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 150):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )

    def split(self, documents: List[Document]) -> List[Document]:
        """
        Split a list of Documents into smaller chunks.
        Metadata (access tag, source_file) is preserved on every chunk.

        Args:
            documents: List of LangChain Document objects from PDFParser.

        Returns:
            Larger list of smaller Document chunks ready for embedding.
        """
        chunks = self.splitter.split_documents(documents)
        return chunks

    def get_embeddings(self) -> OpenAIEmbeddings:
        """
        Returns a configured OpenAIEmbeddings instance using
        the text-embedding-3-small model (1536 dimensions).
        This model is optimised for Pinecone cosine similarity search.
        """
        return OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=os.environ.get("OPENAI_API_KEY", "")
        )
