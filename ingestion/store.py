import chromadb
# import os
import json
from typing import List
from chunker import Chunk
# from sentence_transformers import SentenceTransformer
import sqlite3



def get_chroma_client():
    return chromadb.PersistentClient(path=r"C:\Users\Bakwowi Junior\Documents\My-Portfolio\Automotive Process Intelligence Agent\data\chroma_db")


def create_get_collection(client, name: str = "automotive_docs"):
    return client.get_or_create_collection(
        name=name, 
        embedding_function=None
        )

def store_in_chromadb(chunks: Chunk, embeddings: List[List[float]], collection_name: str = "automotive_docs"):
    client = get_chroma_client()
    collection = create_get_collection(client, collection_name)

    ids, texts, metas, vecs = [], [], [], []

    for chunk, embedding in zip(chunks, embeddings):
            ids.append(chunk.chunk_id)
            texts.append(chunk.text)
            metas.append(chunk.metadata)
            vecs.append(embedding)

    if ids:
        collection.upsert(ids=ids, documents=texts, metadatas=metas, embeddings=vecs)
        print(f"    Stored {len(ids)} chunks in '{collection_name}' collection")



def setup_database():
    """Creates tables if they don't exist."""

    DATABASE_PATH = r"C:\Users\Bakwowi Junior\Documents\My-Portfolio\Automotive Process Intelligence Agent\data\sqlLite_db\apia_db.db"

    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_chunks (
                chunk_id        TEXT PRIMARY KEY,
                doc_title       TEXT,
                doc_type        TEXT,
                file_path       TEXT,
                page_num        INTEGER,
                chunk_index     INTEGER,
                text            TEXT,
                metadata        JSON,
                created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS defect_reports (
                report_id       TEXT PRIMARY KEY,
                input_data      JSON,
                report_data     JSON,
                status          TEXT DEFAULT 'pending',
                human_feedback  TEXT,
                created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_traces (
                trace_id        TEXT PRIMARY KEY,
                report_id       TEXT,
                node_name       TEXT,
                input_tokens    INTEGER,
                output_tokens   INTEGER,
                latency_ms      INTEGER,
                tool_calls      JSON,
                created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")
        
        conn.commit()
    print("---- Database tables ready. ----")


def store_chunks_in_sqlLite(chunks: List[Chunk]):
    """Stores raw chunk text and metadata in sqlLite for full retrieval."""

    DATABASE_PATH = r"C:\Users\Bakwowi Junior\Documents\My-Portfolio\Automotive Process Intelligence Agent\data\sqlLite_db\apia_db.db"

    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        for chunk in chunks:
            cursor.execute("""
                INSERT INTO document_chunks
                    (chunk_id, doc_title, doc_type, file_path, page_num,
                     chunk_index, text, metadata)
                VALUES
                    (:chunk_id, :doc_title, :doc_type, :file_path, :page_num,
                     :chunk_index, :text, :metadata)
                ON CONFLICT (chunk_id) DO UPDATE
                    SET text = EXCLUDED.text,
                        metadata = EXCLUDED.metadata""", {
                "chunk_id": chunk.chunk_id,
                "doc_title": chunk.doc_title,
                "doc_type": chunk.doc_type,
                "file_path": chunk.file_path,
                "page_num": chunk.page_num,
                "chunk_index": chunk.chunk_index,
                "text": chunk.text,
                "metadata": json.dumps(chunk.metadata)
            })
        
        conn.commit()
    print(f"  Stored {len(chunks)} chunks in PostgreSQL.")






