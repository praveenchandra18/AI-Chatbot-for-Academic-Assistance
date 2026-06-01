from hashlib import sha256
from langchain_text_splitters import RecursiveCharacterTextSplitter

def normalise_text(text):
    return " ".join(text.split()).strip()

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
    chunk_id = sha256(text_to_hash.encode('utf-8')).hexdigest()
    return chunk_id

