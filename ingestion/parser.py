from pathlib import Path
import pymupdf
import os
from dataclasses import dataclass
from typing import List
import tqdm


@dataclass
class ParsedDocument:
    file_path: str
    doc_type: str         
    title: str
    pages: List[dict]
    metadata: dict

# file_path = Path(r"C:\Users\Bakwowi Junior\Documents\My-Portfolio\Automotive Process Intelligence Agent\data\documents\tsbs\Clunking sounds and vehicle jerking at slow speeds with large steering angle.pdf")
# print(file_path.name)
# print(type(file_path))

def parse_document(file_path: object, doc_type: str) -> ParsedDocument:

    """
        Get the pdf and extract all the text and tables
    """
    print(f"----Parsing the document {file_path.name}----")
    doc = pymupdf.open(file_path)

    results = dict()
    results["file_path"] = os.path.relpath(file_path)
    results["doc_type"] = doc_type
    results["title"] = file_path.name.strip(".pdf")
    results["pages"] = []
    results["metadata"] = {
        "file_name": file_path.name,
        "total_pages": doc.page_count,
        "doc_type": doc_type
    }

    pages = []
    has_tables = False

    for page_num, page in tqdm.tqdm(enumerate(doc, start=1), desc="doc parsing progress"):
        text = page.get_text("text").strip()

        tables = []

        try:
            tables_finder = page.find_tables()
            if tables_finder:
                has_tables = True

            for table in tables_finder:
                data = table.extract()
                tables.append(data)

        except Exception:
            pass

        pages.append({
            "page_num": page_num,
            "text": text,
            "tables": tables
        })

    doc.close()
    return ParsedDocument(
        file_path=os.path.relpath(file_path),
        doc_type=doc_type,
        title=file_path.name,
        pages=pages,
        metadata={
            "filename": file_path.name,
            "total_pages": len(pages),
            "doc_type": doc_type,
            "has_tables": has_tables
        }
    )




def parse_all_documents(documents_dir) -> List[ParsedDocument]:
    docs = []
    for pdf_path in Path(documents_dir).glob("**/*.pdf"):
        # print(f"  Parsing: {pdf_path.name}")
        try:
            doc = parse_document(pdf_path, pdf_path.parent.name)
            docs.append(doc)
        except Exception as e:
            print(f"  ERROR parsing {pdf_path.name}: {e}")
    return docs




# ParsedDocument
# ├── file_path:   "data/documents/tsb/BMW_P0300.pdf"
# ├── doc_type:    "tsb"
# ├── title:       "BMW Engine Misfire Service Information"
# ├── pages:
# │   ├── page 1: { text: "...", tables: [] }
# │   ├── page 2: { text: "...", tables: [[ {Part: "Coil", PN: "12131354356"} ]] }
# │   └── page 3: { text: "...", tables: [] }
# └── metadata:    { filename: "BMW_P0300.pdf", total_pages: 3, doc_type: "tsb" }
# print(get_parsed_document(file_path, "tsb"))

