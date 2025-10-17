from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    token: str
    type: str 

class TokenData(BaseModel):
    id: Optional[int] = None