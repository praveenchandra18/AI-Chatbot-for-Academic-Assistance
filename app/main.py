from fastapi import FastAPI,Request,Form,HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse,RedirectResponse,StreamingResponse
from contextlib import asynccontextmanager
from app.database import engine,create_db_and_tables
from sqlmodel import Session,select,desc
from app.models import User, Chat, Message
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
from app.utils.password import hash_password
from app.config import SECRET_KEY
from app.security.authentication import authenticate_user,create_jwt_token,verify_jwt
from datetime import datetime
from app.utils.database import get_user_ui_info,add_message,stream_and_save
from app.utils.database import create_new_user,create_new_chat,get_chat_history
from app.utils.database import UserAlreadyExists,UserDoNotExists,PasswordIncorrect
from src.llm import ask
from fastapi import Body

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(
    lifespan=lifespan
)

templates = Jinja2Templates(directory="app/templates")
app.mount("/static",StaticFiles(directory="app/static"),name="static")
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY
)

@app.get("/")
def index():
    return FileResponse("app/static/html/index.html")

@app.get("/login")
def login(request:Request):
    if not verify_jwt(request):
        print("token is not fine")
        return templates.TemplateResponse(
            request,
            "login.html",
            {
                "message":None
            }
        )
    print("token is fine")
    return RedirectResponse(
            url="/chat",
            status_code=303
        )

@app.get("/signup")
def signup_page():
    return FileResponse("app/static/html/signup.html")

@app.post("/signup")
def add_user(
    name:str = Form(...),
    email:str = Form(...),
    password:str = Form(...)
):
    hashed_password = hash_password(password)

    try:
        create_new_user(name,email,hashed_password)
    except UserAlreadyExists as e:
        return "<p>User already Exists</p>"
    except Exception as e:
        print(f"Got error: {e}")
    
    return RedirectResponse(
        url="/login",
        status_code=303
    )


@app.post("/login")
def check_user(
        request:Request,
        email:str = Form(...),
        password:str = Form(...)
    ): 
    try:
        user = authenticate_user(email,password)
    except UserDoNotExists as e:
        return templates.TemplateResponse(
            request,
            "login.html",
            {
                "message": e
            }
        )
    except PasswordIncorrect as e:
        return templates.TemplateResponse(
            request,
            "login.html",
            {
                "message": e
            }
        )
    
    jwt_token = create_jwt_token(user.id)
    response = RedirectResponse(
        url="/chat",
        status_code=303
    )
    response.set_cookie(
        key="access_token",
        value=jwt_token,
        httponly=True
    )
    return response

@app.get("/logout")
def logout():
    response = RedirectResponse(
        url="/login",
        status_code=303
    )
    response.delete_cookie("access_token")
    return response      

@app.get("/chat")
def chat_page(request: Request):
    user_id = verify_jwt(request)
    print(user_id)
    if not user_id:
        return RedirectResponse(
            url="/login",
            status_code=303
        )
    user,chats,messages,current_chat = get_user_ui_info(user_id)
    return templates.TemplateResponse(
        request,
        "chat.html",
        {
            "user":user,
            "messages": messages,
            "chats": chats,
            "current_chat":current_chat
        }
    )

@app.post("/new-chat")
def new_chat(
        request:Request,
        data:dict = Body(...)
        # title:str = Form(...)
        # message:str = Form(...)
    ):
    user_id = verify_jwt(request)
    if not user_id:
        return RedirectResponse(
            url="/login",
            status_code=303
        )
    
    chat_id = create_new_chat(user_id,data["title"])
    return {
            "chat_id": chat_id,
            "title": data["title"]
        }


@app.get("/chat/{chat_id}")
def get_chat(
        chat_id : int,
        request : Request
    ):
    user_id = verify_jwt(request)
    print("User id ",user_id)
    if not user_id:
        return RedirectResponse(
            url="/login",
            status_code=303
        )
    user,chats,messages,current_chat = get_user_ui_info(user_id,chat_id)
    return templates.TemplateResponse(
        request,
        "chat.html",
        {
            "user":user,
            "messages": messages,
            "chats": chats,
            "current_chat":current_chat
        }
    )
    

@app.post("/chat/{chat_id}")
async def send_message(
    chat_id:int,
    request:Request,
    data:dict = Body(...)
):
    user_id = verify_jwt(request)
    if not user_id:
        return RedirectResponse(
            url="/login",
            status_code=303
        )
    chat_history = get_chat_history(chat_id)
    response = await ask(data["message"],chat_history)
    add_message(chat_id,"User",data["message"])
    return StreamingResponse(
        stream_and_save(response,chat_id),
        media_type="text/plain"
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="localhost",
        port=8000,
        reload=True
    )