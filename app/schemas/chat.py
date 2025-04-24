from pydantic import Field

from app.models.base import BaseModel


class ChatBase(BaseModel):
    role: str = Field(
        default="user", examples=["user"], description="role of the message"
    )
    message: str = Field(..., examples=["hello"], description="message content")
