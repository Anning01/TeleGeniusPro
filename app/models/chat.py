from typing import Optional
from sqlmodel import Field

from app.models.base import BaseModel


class Chat(BaseModel, table=True):
    user_id: Optional[int|None] = Field(default=None, foreign_key="user.id")
    message: str
