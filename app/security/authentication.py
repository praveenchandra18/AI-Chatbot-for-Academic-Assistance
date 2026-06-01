from datetime import datetime, timedelta
from fastapi import Request
from sqlmodel import Session,select
from app.models import User
from app.utils.password import verify_password
import jwt
from app.database import engine
from app.config import SECRET_KEY,HASH_ALGORITHM
from datetime import datetime
from app.utils.database import PasswordIncorrect,UserDoNotExists

def create_jwt_token(user_id):
    payload = {
        "user_id" : user_id,
        "exp" : datetime.now()+timedelta(hours=2)
    }
    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm = HASH_ALGORITHM
    )
    return token


def verify_jwt(request:Request):
    token = request.cookies.get("access_token")
    if token is None:
        return None
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[HASH_ALGORITHM]
        )
        return payload.get("user_id")
    
    except Exception as e:
        print(f"Exception at authentication: {e}")
        None

def authenticate_user(email,password) -> User:
    with Session(engine) as session:
        statement = select(User).where(
            User.email == email
        )
        user = session.exec(statement).first()
        if user is None:
            raise UserDoNotExists(
                "Email do not exists"
            )
        
        if not verify_password(password,user.hashed_password):
            raise PasswordIncorrect(
                "Invalid Password"
            )
        
    return user
