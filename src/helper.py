from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_core.documents import Document
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
import os
from dotenv import load_dotenv

load_dotenv()

print("Building Embedding model: ",end="")
embedding_model = OllamaEmbeddings(model="nomic-embed-text")
print("Done")
print("Building Vector db: ",end="")
vector_db = Chroma(collection_name="pdf_texts", 
                   embedding_function=embedding_model,
                   persist_directory="./chroma_db")
print("Done")
print("Building LLM Model: ",end="")
llm = ChatOllama(model=os.getenv("LLM_MODEL"),
                 temperature=0.2,
                 max_tokens=512,
                 validate_model_on_init=True)
print("Done")
print("Building Retrievers: ",end="")
vector_retriever = vector_db.as_retriever(
    search_kwargs={"k": 5}
)

chunks = vector_db.get()
documents = [Document(
    page_content=text,
    metadata = metadata)
    for text,metadata in zip(
        chunks["documents"],
        chunks["metadatas"]
    )
]
bm25_retriever = BM25Retriever.from_documents(documents)
bm25_retriever.k = 5

hybrid_retriever = EnsembleRetriever(
    retrievers=[vector_retriever,
                bm25_retriever],
    weights=[0.5,0.5]
)
print("Done")

print("Building Reranker model: ",end="")
re_ranker_model = HuggingFaceCrossEncoder(
    model_name = "BAAI/bge-reranker-base"
)

compressor = CrossEncoderReranker(
    model= re_ranker_model,
    top_n= 5
)

compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=hybrid_retriever
)
print("Done")

def get_retriever():
    return compression_retriever

def get_vector_db():
    return vector_db

def get_llm_model():
    return llm


