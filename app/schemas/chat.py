from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .user import UserResponse


class ChatBase(BaseModel):
    title: Optional[str] = None

class ChatCreate(ChatBase):
    pass

class ChatResponse(ChatBase):
    id: int
    user: UserResponse
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}