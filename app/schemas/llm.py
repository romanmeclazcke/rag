from pydantic import BaseModel
from typing import Optional, List

class LlmQuestion(BaseModel):
    question: str
    context: Optional[List[str]] = None
    conversation: Optional[List[str]] = None
    
class UserQuestion(BaseModel):
    question: str