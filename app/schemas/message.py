from pydantic import BaseModel
from datetime import datetime
from .chat import ChatResponse


class MessageCreate(BaseModel):
    content: str

class MessageResponse(BaseModel):
    id: int
    chat: ChatResponse 
    content: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}