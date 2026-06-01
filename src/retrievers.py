from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_classic.chains import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.config import RERANKER_MODEL
# from src.vectorstore import get_vector_db

def build_retriever(vector_db):
    # vector_db = get_vector_db()
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

    compressor = CrossEncoderReranker(
        model= re_ranker_model,
        top_n= 5
    )

    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=hybrid_retriever
    )
    print("Done")
    # return compression_retriever
    return hybrid_retriever,re_ranker_model


def build_history_aware_retriever(llm, compression_retriever):
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                Given a chat history and the latest user question,
                formulate a standalone question which can be understood
                without the chat history.

                Do NOT answer the question.
                Only rewrite it if needed.
                """
            ),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ]
    )

    retriever =  create_history_aware_retriever(
        llm=llm,
        retriever=compression_retriever,
        prompt=contextualize_q_prompt
    )

    return retriever
