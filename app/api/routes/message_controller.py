from datetime import datetime, timezone
from typing import List
from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session, selectinload
from dependencies.database import get_db
from schemas.message import MessageCreate, MessageResponse
from model.chat import Chat
from model.message import Message
from utils import oauth2



router = APIRouter(prefix="/messages", 
                   tags=['Messages']) 

@router.get("/{chat_id}", response_model=List[MessageResponse])
def get_messages_by_chat(chat_id: int, db: Session = Depends(get_db)): 
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    messages = db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at.asc()).all()
    return messages

@router.post("/{chat_id}", status_code = status.HTTP_201_CREATED, response_model=MessageResponse) 
def new_message(chat_id: int, message: MessageCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    msg = Message(chat_id=chat_id, content=message.content, role="user")
    
    chat.messages.append(msg) # type: ignore
    chat.updated_at = datetime.now(timezone.utc) # type: ignore

    db.commit()
    db.refresh(msg)

    return msg