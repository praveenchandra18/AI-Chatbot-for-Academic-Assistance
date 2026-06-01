from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Message(SQLModel,table=True):
    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )
    role:str
    chat_id: int = Field(
        foreign_key="chat.id"
    )
    content:str
    