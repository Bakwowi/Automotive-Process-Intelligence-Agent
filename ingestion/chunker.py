from parser import ParsedDocument, parse_document
from langchain_text_splitters import RecursiveCharacterTextSplitter
# from pathlib import Path
from typing import List
from dataclasses import dataclass
import tqdm


@dataclass
class Chunk:
    chunk_id: str
    doc_title: str
    doc_type: str
    file_path: str
    page_num: int
    text: str
    chunk_index: int
    metadata: dict

def text_splitter(text: str, chunk_size: int = 400, overlap: int = 64) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        length_function=len,
        is_separator_regex=False
    )

    chunks = splitter.split_text(text)
    # print(type(chunks), len(chunks))
    # print(chunks[0])

    return chunks


def chunk_document(doc: ParsedDocument) -> List[Chunk]:
    """
        Converts a parsed document into overlapping chunks ready for embedding.
        Tables are serialised to plain text so they get embedded too.
    """

    chunks = []
    chunk_index = 0

    for page in tqdm.tqdm(doc.pages):
        table_text = ""
        for table in page["tables"]:
            for row in table:
                # print(row)
                table_text += "|" + " | ".join([str(i) for i in row]) + "\n"

        full_page_text = page["text"]
        if table_text:
            full_page_text += "\n\nTABLE DATA:\n" + table_text

        if not full_page_text.strip():
            continue

        text_chunks = text_splitter(full_page_text)

        for chunk_text in text_chunks:
            if len(chunk_text.strip()) < 50:
                continue

            chunk_id = f"{doc.metadata['filename']}_p{page['page_num']}_c{chunk_index}"

            chunks.append(Chunk(
                chunk_id=chunk_id,
                doc_title=doc.title,
                doc_type=doc.doc_type,
                file_path=doc.file_path,
                page_num=page["page_num"],
                text=chunk_text.strip(),
                chunk_index=chunk_index,
                metadata={
                    "source": doc.metadata["filename"],
                    "title": doc.title,
                    "doc_type": doc.doc_type,
                    "page": page["page_num"],
                    "has_tables": doc.metadata["has_tables"]
                }
            ))
            chunk_index += 1

    return chunks

