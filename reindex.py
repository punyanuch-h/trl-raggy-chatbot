"""
reindex.py — Admin Re-Indexing CLI Utility for Raggy Bot
=========================================================
Satisfies Business Requirement FR-05:
"The system shall provide a mechanism for Admins to trigger a re-indexing
of the vector database when new PDFs are added or removed."

Usage (Admin runs this from the project root):
    python reindex.py

This script:
1. Scans both source/ and source/private/ for ALL *.pdf files.
2. Parses each PDF using PDFParser (attaches access metadata tag).
3. Splits documents into chunks with TextChunker.
4. Embeds and uploads all chunks into Pinecone with VectorUploader
   (automatically injecting role='admin' for private chunks).
"""

import glob
from pinecone_manager import PineconeManager
from pdf_parser import PDFParser
from text_chunker import TextChunker
from vector_uploader import VectorUploader


class Reindexer:
    """
    Full re-indexing pipeline for the Raggy Bot vector database.
    Scans all PDF sources and re-uploads every document to Pinecone.
    """

    def __init__(self):
        self.pinecone_manager = PineconeManager()
        self.parser = PDFParser()
        self.chunker = TextChunker()
        self.uploader = VectorUploader(pinecone_manager=self.pinecone_manager)

    def run(self):
        """
        Discovers all PDF files from source/ and source/private/,
        processes each through the full ingestion pipeline, and
        uploads the resulting vectors to Pinecone.
        """
        print("[Reindexer] Starting full re-index of Raggy Bot knowledge base...")

        # Discover all PDFs from both public and private source folders
        all_pdfs = glob.glob("source/**/*.pdf", recursive=True)

        if not all_pdfs:
            print("[Reindexer] WARNING: No PDF files found in source/ directories.")
            return

        print(f"[Reindexer] Found {len(all_pdfs)} PDF file(s) to process.")

        for pdf_path in all_pdfs:
            print(f"[Reindexer] Processing: {pdf_path}")

            # Parse: extract text and tag access level (public/private)
            documents = self.parser.load(pdf_path)

            # Chunk: split into manageable pieces preserving metadata
            chunks = self.chunker.split(documents)

            # Upload: embed and upsert into Pinecone (with RBAC injection)
            self.uploader.upload(chunks)

            print(f"[Reindexer] ✓ Completed: {pdf_path} ({len(chunks)} chunks uploaded)")

        print("[Reindexer] Re-index complete. Pinecone knowledge base is up to date.")


if __name__ == "__main__":
    Reindexer().run()
