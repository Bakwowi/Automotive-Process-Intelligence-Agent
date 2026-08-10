import os
import time
from typing import List
from chunker import Chunk
from sentence_transformers import SentenceTransformer


def embed_chunks(chunks: List[Chunk], batch_size: int = 128) -> List[List[float]]:

    embedder = SentenceTransformer("all-MiniLM-L6-v2") # or BAAI/bge-m3
    print("hello world")