from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class BaseModel(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)