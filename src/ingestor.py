import fitz
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path
from langchain_core.documents import Document
import hashlib
from src.helper import get_vector_db

def normalise_text(text):
    return " ".join(text.split()).strip()

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

def extract_chunks_from_docs(docs, chunk_size=500, overlap=50):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(docs)
    return chunks

def create_chunk_id(chunk,chunk_index):
    normalised_text = normalise_text(chunk.page_content)
    text_to_hash = f"{chunk.metadata['source']}|{chunk.metadata['page']}|{chunk_index}|{normalised_text}"
    # We get the text, make them into raw bites and hash them. Then we make it into readable hex string
    chunk_id = hashlib.sha256(text_to_hash.encode('utf-8')).hexdigest()
    return chunk_id

def add_chunks_to_vector_db(chunks):
    try:
        vector_db = get_vector_db()

        chunk_ids = set(vector_db.get(include=[])["ids"])
        new_chunks = []
        new_ids = []
        for i, chunk in enumerate(chunks):
            chunk_id = create_chunk_id(chunk, i)
            if(chunk_id not in chunk_ids):
                new_chunks.append(chunk)
                new_ids.append(chunk_id)

        if new_chunks:
            vector_db.add_documents(new_chunks, ids=new_ids)
        return True
    except Exception as e:
        print(f"Error adding chunks to vector DB: {e}")
        return False

def add_pdf_to_vector_db(pdf_path):
    docs = extract_docs_from_pdf(pdf_path)
    chunks = extract_chunks_from_docs(docs)
    if add_chunks_to_vector_db(chunks):
        print(f"Successfully added chunks from {pdf_path} to vector DB.")

if __name__ == "__main__":
    pdf_path = "data/MACHINE LEARNING.pdf"
    add_pdf_to_vector_db(pdf_path)