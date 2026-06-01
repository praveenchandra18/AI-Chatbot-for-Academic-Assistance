from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Chat(SQLModel,table=True):
    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )
    title:str
    user_id: int = Field(
        foreign_key="user.id"
    )
    created_at: datetime = Field(
        default_factory=datetime.now
    )