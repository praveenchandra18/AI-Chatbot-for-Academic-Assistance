from sqlmodel import Session,select,desc
from app.database import engine
from app.models import User, Chat, Message 
from langchain_core.messages import HumanMessage,AIMessage

class UserAlreadyExists(Exception):
    pass

class UserDoNotExists(Exception):
    pass

class PasswordIncorrect(Exception):
    pass

def create_new_user(name,email,hashed_password):
    with Session(engine) as session:
        statement = select(User).where(
            User.email == email
        )
        user = session.exec(statement).first()
        if(user):
            raise UserAlreadyExists(
                "Email Already Exists"
            )
        user = User(
            name = name,
            email = email,
            hashed_password = hashed_password
        )
        session.add(user)
        session.commit()
        session.refresh(user)

def get_user_ui_info(user_id,chat_id=None):
    with Session(engine) as session:
        user = session.get(User,user_id)
        chats = get_chats(user_id,decreasing_order=True)
        # DEFAULT VALUES
        current_chat = None
        messages = []
        if chat_id:
            current_chat = get_chat(user_id,chat_id)
            if current_chat:
                messages = get_messages(current_chat.id)
            return user,chats,messages,current_chat
        # GET LAST CHAT
        if chats:
            current_chat = chats[0]
            messages = get_messages(current_chat.id)
    return user,chats,messages,current_chat

def get_chat(user_id,chat_id):
    with Session(engine) as session:
        chat = session.exec(
            select(Chat)
            .where(Chat.user_id==user_id, Chat.id == chat_id)
        ).first()

    return chat

def get_chats(user_id,decreasing_order=False):
    with Session(engine) as session:
        if decreasing_order:
            chats = session.exec(
                select(Chat)
                .where(Chat.user_id == user_id)
                .order_by(desc(Chat.id))
                ).all()
        else:
            chats = session.exec(
                select(Chat).where(
                    Chat.user_id == user_id
                )
            ).all()
    return chats

def get_messages(chat_id):
    with Session(engine) as session:
        messages = session.exec(
            select(Message).where(
                Message.chat_id==chat_id,
            )
        ).all()
    return messages

def create_new_chat(user_id,title):
    with Session(engine) as session:
        # user = session.get(User,user_id)
        chat = Chat(
            title=title,
            user_id=user_id
        )

        session.add(chat)
        session.commit()
        session.refresh(chat)

        return chat.id


def add_message(chat_id,role,content):
    with Session(engine) as session:
        mess_obj = Message(
            chat_id=chat_id,
            role=role,
            content=content
        )
        session.add(mess_obj)
        session.commit()
        session.refresh(mess_obj)

async def stream_and_save(response,chat_id):
    full_response = ""
    async for chunk in response:
        full_response+=chunk
        yield chunk

    add_message(chat_id,"AI Assistant",full_response)

def get_chat_history(chat_id,limit=20):
    with Session(engine) as session:
        messages = session.exec(
            select(Message)
            .where(Message.chat_id==chat_id)
            .order_by(Message.id.desc())
            .limit(limit)
        ).all()

    messages = list(reversed(messages))
    chat_history = []

    for message in messages:
        if message.role == "User":
            chat_history.append(
                HumanMessage(content=message.content)
            )

        elif message.role == "AI Assistant":
            chat_history.append(
                AIMessage(content=message.content)
            )
    
    print("printing chat history here")
    for message in chat_history:
        print(message)
    return chat_history