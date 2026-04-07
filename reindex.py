"""
reindex.py - Admin re-indexing CLI utility for Raggy Bot.

Supports source discovery for `.pdf` and `.txt` files under `source/`
and `source/private/`, then parses, chunks, and uploads them to Pinecone.
"""

from __future__ import annotations

from pathlib import Path

from pinecone_manager import PineconeManager
from source_document_parser import SourceDocumentParser
from text_chunker import TextChunker
from vector_uploader import VectorUploader


SUPPORTED_SOURCE_EXTENSIONS = {".pdf", ".txt"}
SOURCE_ROOT = Path("source")


def discover_source_files(root: Path = SOURCE_ROOT) -> list[str]:
    discovered: list[str] = []
    for path in root.rglob("*"):
        if not getattr(path, "suffix", ""):
            path = Path(path)
        if path.is_dir():
            continue
        if path.suffix.lower() in SUPPORTED_SOURCE_EXTENSIONS:
            discovered.append(path.as_posix())
        else:
            print(f"[Reindexer] Skipping unsupported file: {path.as_posix()}")
    return sorted(discovered)


class Reindexer:
    """
    Full re-indexing pipeline for the Raggy Bot vector database.
    Scans supported source files and re-uploads every document to Pinecone.
    """

    def __init__(self):
        self.pinecone_manager = PineconeManager()
        self.parser = SourceDocumentParser()
        self.chunker = TextChunker()
        self.uploader = VectorUploader(pinecone_manager=self.pinecone_manager)

    def run(self):
        print("[Reindexer] Starting full re-index of Raggy Bot knowledge base...")

        all_source_files = discover_source_files()
        if not all_source_files:
            print("[Reindexer] WARNING: No supported source files found in source/ directories.")
            return

        print(f"[Reindexer] Found {len(all_source_files)} supported file(s) to process.")

        for source_path in all_source_files:
            suffix = Path(source_path).suffix.lower()
            if suffix not in SUPPORTED_SOURCE_EXTENSIONS:
                print(f"[Reindexer] Skipping unsupported file: {source_path}")
                continue

            print(f"[Reindexer] Processing: {source_path}")
            documents = self.parser.load(source_path)
            chunks = self.chunker.split(documents)
            self.uploader.upload(chunks)
            print(f"[Reindexer] Completed: {source_path} ({len(chunks)} chunks uploaded)")

        print("[Reindexer] Re-index complete. Pinecone knowledge base is up to date.")
