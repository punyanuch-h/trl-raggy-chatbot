import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


class PDFParser:
    """
    Handles loading and pre-processing of PDF files for Raggy Bot.

    Responsibilities:
    - Uses LangChain's PyPDFLoader to extract text from PDF files.
    - Detects whether the PDF originates from the restricted
      'source/private' directory and tags it accordingly.

    Metadata Tags:
    - {"access": "public"}  -> Accessible to all roles (researcher, admin)
    - {"access": "private"} -> Restricted to admin role only (RBAC enforcement)
    """

    def load(self, file_path: str) -> List[Document]:
        """
        Load a PDF from the given file path and return a list of
        LangChain Document objects with correctly tagged metadata.

        Args:
            file_path: Absolute or relative path to the PDF file.

        Returns:
            List of LangChain Document objects.
        """
        # Detect private path (Windows and Unix compatible)
        normalized = file_path.replace("\\", "/")
        access_tag = "private" if "source/private" in normalized else "public"

        # Load using LangChain's PyPDFLoader
        loader = PyPDFLoader(file_path)
        docs = loader.load()

        # Inject the access metadata tag into every extracted chunk
        for doc in docs:
            doc.metadata["access"] = access_tag
            doc.metadata["source_file"] = os.path.basename(file_path)

        return docs
