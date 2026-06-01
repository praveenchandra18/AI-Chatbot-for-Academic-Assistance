from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from src.config import RERANKER_MODEL

def build_retriever(vector_db):
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
    del chunks
    del documents
    print("Done")


    print("Building Reranker model: ",end="")
    re_ranker_model = HuggingFaceCrossEncoder(
        model_name = RERANKER_MODEL
    )

    # compressor = CrossEncoderReranker(
    #     model= re_ranker_model,
    #     top_n= 5
    # )

    # compression_retriever = ContextualCompressionRetriever(
    #     base_compressor=compressor,
    #     base_retriever=hybrid_retriever
    # )
    print("Done")
    return hybrid_retriever,re_ranker_model
