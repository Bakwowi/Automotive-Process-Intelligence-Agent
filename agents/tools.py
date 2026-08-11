import os
import json
# import voyageai
import chromadb
# from tavily import TavilyClient
# from sqlalchemy import create_engine, text
import sqlite3
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

# ── Clients ──────────────────────────────────────────────────────────────────

# _voyage_client = None
_chroma_client = None
_tavily_client = None
# _db_engine = None


# def get_voyage():
#     global _voyage_client
#     if not _voyage_client:
#         _voyage_client = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
#     return _voyage_client


def get_chroma():
    global _chroma_client
    if not _chroma_client:
        _chroma_client = chromadb.PersistentClient(path=r"C:\Users\Bakwowi Junior\Documents\My-Portfolio\Automotive Process Intelligence Agent\data\chroma_db")
    return _chroma_client


# def get_tavily():
#     global _tavily_client
#     if not _tavily_client:
#         _tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
#     return _tavily_client


# def get_db():
#     global _db_engine
#     if not _db_engine:
#         _db_engine = create_engine(os.getenv("DATABASE_URL"))
#     return _db_engine


# ── Tool implementations ──────────────────────────────────────────────────────

def search_vector_store(query: str, n_results: int = 5, doc_type: str = None) -> dict:
    """
    Searches the general automotive documentation vector store.
    Returns the top-n most relevant chunks.
    """
    try:
        query_embedding = SentenceTransformer().encode_query(query)

        chroma = get_chroma()
        collection = chroma.get_collection("automotive_docs")

        where_filter = {"doc_type": doc_type} if doc_type else None

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )

        chunks = []
        for i, doc in enumerate(results["documents"][0]):
            chunks.append({
                "text": doc,
                "source": results["metadatas"][0][i].get("source"),
                "page": results["metadatas"][0][i].get("page"),
                "doc_type": results["metadatas"][0][i].get("doc_type"),
                "relevance_score": round(1 - results["distances"][0][i], 3)
            })

        return {"success": True, "query": query, "results": chunks}

    except Exception as e:
        return {"success": False, "error": str(e), "query": query}


def search_standards_db(query: str, n_results: int = 5) -> dict:
    """
    Searches only the automotive standards collection
    (ISO, IATF 16949, BMW group standards).
    """
    try:
        query_embedding = SentenceTransformer().encode_query(query)

        chroma = get_chroma()
        collection = chroma.get_collection("standards")

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )

        chunks = []
        for i, doc in enumerate(results["documents"][0]):
            chunks.append({
                "text": doc,
                "source": results["metadatas"][0][i].get("source"),
                "page": results["metadatas"][0][i].get("page"),
                "relevance_score": round(1 - results["distances"][0][i], 3)
            })

        return {"success": True, "query": query, "results": chunks}

    except Exception as e:
        return {"success": False, "error": str(e), "query": query}


def fetch_document_section(source_filename: str, page_num: int) -> dict:
    """
    Retrieves the full text of a specific page from a document.
    Use after search_vector_store when you need the full context around a chunk.
    """
    try:
        DATABASE_PATH = r"C:\Users\Bakwowi Junior\Documents\My-Portfolio\Automotive Process Intelligence Agent\data\sqlLite_db\apia_db.db"
        
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            rows = cursor.execute("""
                SELECT text, doc_title, doc_type, chunk_index
                FROM document_chunks
                WHERE metadata->>'source' = :source
                  AND page_num = :page_num
                ORDER BY chunk_index ASC
            """, {"source": source_filename, "page_num": page_num})

            chunks = rows.fetchall()

        if not chunks:
            return {
                "success": False,
                "error": f"No content found for {source_filename} page {page_num}"
            }

        full_text = "\n".join(row[0] for row in chunks)
        return {
            "success": True,
            "source": source_filename,
            "page_num": page_num,
            "doc_title": chunks[0][1],
            "full_text": full_text
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


# def web_search(query: str, max_results: int = 5) -> dict:
#     """
#     Searches the web for current information — use for recent
#     regulatory updates, recall notices, or technical bulletins
#     not yet in the local knowledge base.
#     """
#     try:
#         tavily = get_tavily()
#         results = tavily.search(
#             query=query,
#             max_results=max_results,
#             search_depth="advanced"
#         )

#         formatted = []
#         for r in results.get("results", []):
#             formatted.append({
#                 "title": r.get("title"),
#                 "url": r.get("url"),
#                 "content": r.get("content", "")[:500]  # Truncate for context
#             })

#         return {"success": True, "query": query, "results": formatted}

#     except Exception as e:
#         return {"success": False, "error": str(e), "query": query}


# ── Tool dispatch ─────────────────────────────────────────────────────────────

def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Routes a tool call to the right function. Returns JSON string."""
    dispatch = {
        "search_vector_store": search_vector_store,
        "search_standards_db": search_standards_db,
        "fetch_document_section": fetch_document_section
        # "web_search": web_search,
    }
    if tool_name not in dispatch:
        return json.dumps({"success": False, "error": f"Unknown tool: {tool_name}"})

    result = dispatch[tool_name](**tool_input)
    return json.dumps(result)


# ── Tool schemas (what Claude reads) ─────────────────────────────────────────

RESEARCHER_TOOLS = [
    {
        "name": "search_vector_store",
        "description": (
            "Searches the automotive documentation knowledge base (TSBs, repair manuals, "
            "guides) using semantic similarity. Use this to find relevant procedures, "
            "known issues, part numbers, and repair steps for a given defect description. "
            "Always call this first before attempting to answer from memory."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "A specific technical query describing the defect or the information needed."
                },
                "n_results": {
                    "type": "integer",
                    "description": "Number of results to return. Default 5, max 10.",
                    "default": 5
                },
                "doc_type": {
                    "type": "string",
                    "description": "Filter by doc type: 'tsb', 'manual', or 'guide'. Omit to search all.",
                    "enum": ["tsb", "manual", "standards"]
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "fetch_document_section",
        "description": (
            "Retrieves the full text of a specific page from a document. "
            "Use this after search_vector_store when a chunk looks highly relevant "
            "but you need to read the full page for complete context."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "source_filename": {
                    "type": "string",
                    "description": "The filename of the source document, as returned in search results."
                },
                "page_num": {
                    "type": "integer",
                    "description": "The page number to retrieve, as returned in search results."
                }
            },
            "required": ["source_filename", "page_num"]
        }
    }
]

VALIDATOR_TOOLS = [
    {
        "name": "search_standards_db",
        "description": (
            "Searches the automotive standards knowledge base (ISO 9001, IATF 16949, "
            "BMW group standards). Use this to check whether a proposed repair procedure "
            "complies with relevant quality and safety standards."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "A specific query about a standard, clause, or compliance requirement."
                },
                "n_results": {
                    "type": "integer",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    },
    {
        "type": "web_search_20250305",
        "name": "web_search"
        # "description": (
        #     "Searches the web for current information. Use this to check for recent "
        #     "regulatory updates, new recall notices, or standard amendments that may "
        #     "not yet be in the local knowledge base. Always prefer search_standards_db "
        #     "first; use web_search only when the local results are insufficient."
        # )
    }
]