from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class User(SQLModel, table=True):
    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )
    name:str 
    email: str = Field(
        unique=True
    )
    hashed_password: str
    created_at: datetime = Field(
        default_factory=datetime.now
    )

