from __future__ import annotations

import os
from pathlib import Path
from typing import List

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document


class SourceDocumentParser:
    """
    Handles loading supported source files for Raggy Bot.

    Supported formats:
    - `.pdf`
    - `.txt`
    """

    def load(self, file_path: str) -> List[Document]:
        normalized = file_path.replace("\\", "/")
        access_tag = "private" if "source/private" in normalized else "public"
        suffix = Path(file_path).suffix.lower()

        if suffix == ".pdf":
            loader = PyPDFLoader(file_path)
        elif suffix == ".txt":
            loader = TextLoader(file_path, encoding="utf-8")
        else:
            raise ValueError(f"Unsupported source file type: {suffix or file_path}")

        docs = loader.load()
        for doc in docs:
            doc.metadata["access"] = access_tag
            doc.metadata["source_file"] = os.path.basename(file_path)

        return docs
