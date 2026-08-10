from parser import ParsedDocument, parse_document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path
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
                    "doc_type": doc.doc_type,
                    "page": page["page_num"],
                }
            ))
            chunk_index += 1

    return chunks







file_path = Path(r"C:\Users\Bakwowi Junior\Documents\My-Portfolio\Automotive Process Intelligence Agent\data\documents\tsbs\Clunking sounds and vehicle jerking at slow speeds with large steering angle.pdf")

parsed_doc = parse_document(file_path, "tsb")

print(chunk_document(parsed_doc))


# Chunk
# ├── chunk_id:    "BMW_P0300.pdf_p2_c3"   ← unique ID: filename + page + chunk index
# ├── doc_title:   "BMW Engine Misfire Service Information"
# ├── doc_type:    "tsb"
# ├── file_path:   "data/documents/tsb/BMW_P0300.pdf"
# ├── page_num:    2
# ├── text:        "The ignition coil must be replaced using tool 12-1-xxx.
# │                 Torque the bolt to 8 Nm. Do not reuse the old coil
# │                 connector clip as it may..."
# ├── chunk_index: 3
# └── metadata:    { source: "BMW_P0300.pdf", doc_type: "tsb", page: 2 }