from langchain_ollama import ChatOllama
from src.config import LLM_MODEL
from langchain_core.messages import HumanMessage,SystemMessage
from src.vectorstore import get_similar_chunks
from src.config import BASIC_SYSTEM_PROMPT, RE_WRITE_PROMPT, IRRELEVANT_QUESTION_ANSWER

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
    async for token in llm.astream(messages):
        yield token.content

async def yeild_nothing():
    yield IRRELEVANT_QUESTION_ANSWER

def get_restructured_question(question,chat_history):
    re_written_prompt = f"""{RE_WRITE_PROMPT}
    
    Chat History: 
    {chat_history}

    Question: 
    {question}

    """
    return llm.invoke(re_written_prompt)

async def ask(question,chat_history):
    restructured_question = get_restructured_question(question,chat_history)
    similar_chunks =await get_similar_chunks(restructured_question.content)
    if len(similar_chunks)==0:
        return yeild_nothing()
    prompt = generate_prompt(question, similar_chunks, chat_history)
    return call_llm(prompt)
        