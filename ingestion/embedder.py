# import os
# import time
from typing import List
from chunker import Chunk
from sentence_transformers import SentenceTransformer


def embed_chunks(chunks: List[Chunk], batch_size: int = 128) -> List[List[float]]:

    embedder = SentenceTransformer("all-MiniLM-L6-v2") # or BAAI/bge-m3
    texts = [chunk.text for chunk in chunks]

    try:
        all_embeddings = embedder.encode_document(
            inputs=texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
    except Exception as e:
        print(f"An error occured while embedding the chunks -> {e}")


    return all_embeddings



