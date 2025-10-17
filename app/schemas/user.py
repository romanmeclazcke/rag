from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str 

class UserResponse(UserBase): # NO devuelve password!
    id: int 
    created_at: datetime

    model_config = {"from_attributes": True}