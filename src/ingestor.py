import asyncio
from src.extractor import extract_docs_from_pdf
from src.chunker import extract_chunks_from_docs
from src.chunker import create_chunk_id
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from src.config import EMBEDDING_MODEL,PERSISTANT_DIRECTORY_PATH

def get_vector_db():
    embedding_model = OllamaEmbeddings(EMBEDDING_MODEL)
    vector_db = Chroma(collection_name="pdf_texts", 
                       embedding_function=embedding_model,
                       persist_directory=PERSISTANT_DIRECTORY_PATH)
    return vector_db

async def add_pdf_to_vector_db(pdf_path):
    try:
        docs = await asyncio.to_thread(extract_docs_from_pdf,pdf_path)
        chunks =await asyncio.to_thread(extract_chunks_from_docs,docs)
        if await asyncio.to_thread(add_chunks_to_vector_db,chunks):
            print(f"Successfully added chunks from {pdf_path} to vector DB.")
    except Exception as e:
        print(f"Error processing {pdf_path} : {e}")

async def process_all_pdfs(pdf_paths:list):
    await asyncio.gather(
        *(add_pdf_to_vector_db(pdf_path) for pdf_path in pdf_paths)
    )

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

if __name__ == "__main__":
    pdf_paths = ["data/MACHINE LEARNING.pdf"]
    asyncio.run(process_all_pdfs(pdf_paths))