from langchain_ollama import ChatOllama
from src.config import LLM_MODEL
# import asyncio
# from collections import deque
from langchain_core.messages import HumanMessage,SystemMessage,AIMessage
from src.vectorstore import get_similar_chunks,build_history_aware_retriever,hybrid_retriever
from src.config import BASIC_SYSTEM_PROMPT, RE_WRITE_PROMPT

def build_llm():
    print("Building LLM Model: ",end="")
    llm = ChatOllama(model=LLM_MODEL,
                     temperature=0.2,
                     max_tokens=512,
                     validate_model_on_init=True)
    print("Done")
    return llm

llm = build_llm()

def get_llm_model():
    return llm

llm = get_llm_model()

    
def generate_prompt(question, similar_chunks, chat_history):
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
    
async def call_llm(messages):
    # response = llm.invoke(prompt)
    async for token in llm.astream(messages):
        yield token.content
    # return response.content

async def yeild_nothing():
    yield "I dont think i can answer this"

def get_restructured_question(question,chat_history):
    re_written_prompt = f"""{RE_WRITE_PROMPT}
    
    Chat History: 
    {chat_history}

    Question: 
    {question}

    """
    return llm.invoke(re_written_prompt)

async def ask(question,chat_history):
    # print("Extracting data...")
    restructured_question = get_restructured_question(question,chat_history)
    print("Restructured question :" ,restructured_question.content)
    print(type(restructured_question.content))
    similar_chunks =await get_similar_chunks(restructured_question.content)
    print("Similar chunks",similar_chunks)
    if len(similar_chunks)==0:
        return yeild_nothing()
    # filtered_chunks = [chunk for chunk in similar_chunks if chunk.metadata["relevance_score"]>0.7]
    # print("Extraction completed")
    prompt = generate_prompt(question, similar_chunks, chat_history)
    # print("Retrieving answer...")
    # print(prompt)
    print("---------------------------------------------")
    print(similar_chunks)
    print("-------------------------------------------")
    print(prompt)
    print("-------------------------------------------")
    return call_llm(prompt)
        

# async def main():
#     while True:
#         user_input = input("User: ")
#         response =await ask(user_input)
#         print("Assistant: ")
#         total_response=""
#         async for chunk in response:
#             total_response+=chunk.content
#             print(chunk.content,end="",flush=True)
#         print()
        # chat_history.append(HumanMessage(user_input))
        # chat_history.append(AIMessage(total_response))


# if __name__ == "__main__":
    # query = "What is machine learning ?"
    # # print(ask(query))
    # response = ask(query)
    # print("Assistant: ",end="")
    # for chunk in response:
    #     print(chunk.content,end="",flush=True)
    # asyncio.run(main())