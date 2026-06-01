import asyncio
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from src.retrievers import build_retriever,build_history_aware_retriever
from src.config import EMBEDDING_MODEL,PERSISTANT_DIRECTORY_PATH


def build_db():
    print("Embedding model building started: ",end="")
    embedding_model = OllamaEmbeddings(model=EMBEDDING_MODEL)
    print("Done")
    print("Building Vector db: ",end="")
    vector_db = Chroma(collection_name="pdf_texts", 
                       embedding_function=embedding_model,
                       persist_directory=PERSISTANT_DIRECTORY_PATH)
    print("Done")
    return embedding_model,vector_db

embedding_model, vector_db = build_db()

def get_vector_db():
    return vector_db

hybrid_retriever,rerankermodel = build_retriever(vector_db)

async def get_similar_chunks(query):
    try:
        # vector_db = get_vector_db()
        # hybrid_retriever = get_retriever()
        print("Query is :", query)
        print(type(query))
        docs= await hybrid_retriever.ainvoke(query)

        pairs = [[query, doc.page_content]
                for doc in docs]

        scores = rerankermodel.score(pairs)

        for doc, score in zip(docs, scores):
            doc.metadata["rerank_score"] = score
                # results = vector_db.similarity_search(query, k=top_k)

        docs = sorted(
            zip(docs,scores),
            key = lambda x:x[1],
            reverse=True
        )
        top_docs = [doc for doc, score in docs[:5]]
        print("Top score:", docs[0][1])
        if docs[0][1]<0.2:
            return []
        return top_docs
    except Exception as e:
        print(f"Error retrieving similar chunks: {e}")
        return []