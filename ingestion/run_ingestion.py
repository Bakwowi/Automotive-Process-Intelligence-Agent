"""
Run this script to build the knowledge base from PDFs in data/documents/.
Usage: python -m ingestion.run_ingestion
"""
import os
from dotenv import load_dotenv
from parser import parse_all_documents
from chunker import chunk_document
from embedder import embed_chunks
from store import (
    setup_database,
    store_in_chromadb,
    store_chunks_in_sqlLite
)

load_dotenv()
DOCUMENTS_DIR = "data/documents"


def run():
    print("\n=== APIA Ingestion Pipeline ===\n")

    # 1. Setup
    print("[1/5] Setting up database...")
    setup_database()

    # 2. Parse
    print(f"\n[2/5] Parsing PDFs from {DOCUMENTS_DIR}...")

    documents = parse_all_documents(DOCUMENTS_DIR)
    print(f"  Parsed {len(documents)} documents.")

    if not documents:
        print("  No PDFs found. Add PDFs to data/documents/ and re-run.")
        return

    # 3. Chunk
    print("\n[3/5] Chunking documents...")
    all_chunks = []
    for doc in documents:
        chunks = chunk_document(doc)
        all_chunks.extend(chunks)
        print(f"  {doc.title}: {len(chunks)} chunks")
    print(f"  Total chunks: {len(all_chunks)}")

    # 4. Embed
    print("\n[4/5] Generating embeddings (SentenceTransformer)...")
    embeddings = embed_chunks(all_chunks)
    print(f"  Generated {len(embeddings)} embeddings.")

    # 5. Store
    print("\n[5/5] Storing in ChromaDB + sqlLite...")
    store_in_chromadb(all_chunks, embeddings)
    store_chunks_in_sqlLite(all_chunks)

    print("\n=== Ingestion complete. Knowledge base ready. ===\n")


if __name__ == "__main__":
    run()