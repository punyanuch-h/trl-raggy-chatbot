import os
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


class PDFParser:
    """
    Backward-compatible PDF parser for Raggy Bot.
    """

    def load(self, file_path: str) -> List[Document]:
        normalized = file_path.replace("\\", "/")
        access_tag = "private" if "source/private" in normalized else "public"

        loader = PyPDFLoader(file_path)
        docs = loader.load()

        for doc in docs:
            doc.metadata["access"] = access_tag
            doc.metadata["source_file"] = os.path.basename(file_path)

        return docs
