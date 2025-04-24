from typing import Optional

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel, Relationship


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    meta: dict = Field(sa_type=JSONB, nullable=False)
    chat: list["Chat"] = Relationship(back_populates="user")
