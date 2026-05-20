from langchain_ollama import ChatOllama
from src.helper import get_vector_db
from src.helper import get_llm_model
from src.helper import get_retriever
from collections import deque
from langchain_core.messages import HumanMessage,SystemMessage,AIMessage


chat_history = deque(maxlen=20)
BASIC_SYSTEM_PROMPT = SystemMessage(
    content=f"""
You are a knowledgeable academic assistant.

Answer the user's question using ONLY the information
provided in the context below.

Guidelines:
- Do not fabricate information.
- Do not use prior knowledge.
- If the answer cannot be found, say:
  "I don't know based on the provided context."
- Keep answers concise and accurate.
- Do not mention the existence of the context.
- Mention the context source for every piece of information.
"""
)


llm = get_llm_model()

def get_similar_chunks(query, top_k=5):
    try:
        vector_db = get_vector_db()
        hybrid_retriever = get_retriever()
        results = hybrid_retriever.invoke(query)
        # results = vector_db.similarity_search(query, k=top_k)
        return results
    except Exception as e:
        print(f"Error retrieving similar chunks: {e}")
        return []
    
def generate_prompt(question, similar_chunks):
    # context = "\n\n".join([chunk.page_content for chunk in similar_chunks])
    context = "\n\n"
    for chunk in similar_chunks:
        context+=f"""Source: {chunk.metadata["source"]}, Page number: {chunk.metadata["page"]}
                     Content: {chunk.page_content}"""
    system_message = SystemMessage(content=f"""{BASIC_SYSTEM_PROMPT}
                Context:
                {context}
            """)
    messages = [system_message,
                *chat_history,
                HumanMessage(question)]
    
    return messages
    
def call_llm(messages):
    # response = llm.invoke(prompt)
    for token in llm.stream(messages):
        yield token
    # return response.content

def ask(question):
    # print("Extracting data...")
    similar_chunks = get_similar_chunks(question)
    # print("Extraction completed")
    prompt = generate_prompt(question, similar_chunks)
    # print("Retrieving answer...")
    llm_response = call_llm(prompt)
    return llm_response
        

if __name__ == "__main__":
    # query = "What is machine learning ?"
    # # print(ask(query))
    # response = ask(query)
    # print("Assistant: ",end="")
    # for chunk in response:
    #     print(chunk.content,end="",flush=True)
    while True:
        user_input = input("User: ")
        response = ask(user_input)
        print("Assistant: ")
        total_response=""
        for chunk in response:
            total_response+=chunk.content
            print(chunk.content,end="",flush=True)
        print()
        chat_history.append(AIMessage(total_response))