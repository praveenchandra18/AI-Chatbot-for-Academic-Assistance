import fitz
from pathlib import Path
from langchain_core.documents import Document

def extract_docs_from_pdf(pdf_path):
    pdf = fitz.open(pdf_path)
    file_name = Path(pdf_path).name
    docs = []
    for page_num, page in enumerate(pdf):
        text = page.get_text()
        doc = Document(page_content=text,
                       metadata = {
                           "source": f"{file_name}",
                           "page": page_num + 1
                       })
        docs.append(doc)
    return docs