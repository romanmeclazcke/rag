from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, selectinload
from datetime import datetime, timezone
from dependencies.database import get_db, SessionLocal
from schemas.chat import ChatCreate, ChatResponse
from schemas.message import MessageCreate, MessageResponse
from model.chat import Chat
from model.message import Message
from model.user import User
from utils.hash import verify
from utils import oauth2
from services.llm_service import LlmService
from schemas.llm import LlmQuestion
from services.dependencies.embedding_service import get_embedding_service
from services.dependencies.embedding_service import EmbeddingService
from schemas.embedding import EmbeddingText
from services.dependencies.llm_service import get_llm_service

router = APIRouter(prefix="/chats", 
                   tags=['Chats']) 

@router.get("/", response_model=List[ChatResponse])
def get_all_by_user(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    return db.query(Chat).filter(Chat.user_id == current_user.id).all() # type: ignore


@router.get("/{id}", response_model=ChatResponse)
def get_by_user(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):       
    chat = db.query(Chat).filter(Chat.id == id, Chat.user_id == current_user.id).first()# type: ignore
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    
    return chat


@router.post("/", status_code = status.HTTP_201_CREATED, response_model=ChatResponse) 
def new_chat(chat: ChatCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    new_chat = Chat(**chat.model_dump(), user_id = current_user.id) # type: ignore
    db.add(new_chat)
    db.commit() 
    db.refresh(new_chat) 

    return new_chat 


@router.put("/{id}", response_model=ChatResponse) 
def update_chat(id: int, updated_chat: ChatCreate, db: Session = Depends(get_db)):
    find_chat = db.query(Chat).filter(Chat.id == id)
    chat = find_chat.first()
    if not chat:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"Chat with id {id} does not exist")

    find_chat.update(updated_chat.model_dump(), synchronize_session=False) # type: ignore
    db.commit()

    return find_chat.first() 


@router.delete("/{id}", status_code = status.HTTP_204_NO_CONTENT)
def delete_chat(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    find_chat = db.query(Chat).filter(Chat.id == id, Chat.user_id == current_user.id)# type: ignore
    if not find_chat.first():
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"Chat with id {id} does not exist or does not belong to the current user")
    
    find_chat.delete(synchronize_session=False) # opción más eficiente
    db.commit()

    return Response(status_code = status.HTTP_204_NO_CONTENT)


@router.delete("/clear/{id}", status_code=status.HTTP_204_NO_CONTENT)
def clear_chat(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    chat = db.query(Chat).filter(Chat.id == id, Chat.user_id == current_user.id).first()# type: ignore
    if not chat:
        raise HTTPException(status_code=404, detail="Chat does not exist or does not belong to the current user")

    deleted = (db.query(Message).filter(Message.chat_id == id).delete(synchronize_session=False))

    chat.updated_at = datetime.now(timezone.utc) # type: ignore
    db.commit()

    return {"deleted": deleted}


@router.post("/talk/{id}")
async def send_message(id: int, message: MessageCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), embedding_service: EmbeddingService = Depends(get_embedding_service), llm_service: LlmService = Depends(get_llm_service)):
    chat_db = db.query(Chat).options(selectinload(Chat.messages)).filter(Chat.id == id, Chat.user_id == current_user.id).first()# type: ignore
    if not chat_db: # Creo uno nuevo 
        chat_db = Chat(user_id=current_user.id, title="New chat", created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)) # type: ignore
        db.add(chat_db)
        db.commit()
        db.refresh(chat_db)

    # Guardo el msj del usuario
    user_msg = Message(chat_id=chat_db.id, role="user", content=message.content)
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)
    
    # Construyo el historial de conversación
    context = []
    if len(chat_db.messages) == 0:
        context.append({
            "role": "system", # comportamiento
            "content": "Eres un asistente experto, claro y conciso. Responde únicamente en el idioma de la pregunta."
        })

    context += [
        {"role": msg.role, "content": msg.content}
        for msg in chat_db.messages[-10:] # solo los últimos 10 para no sobrecargar tanto
    ] 
    context.append({"role": "user", "content": message.content}) # agrego el nuevo mensaje
    
    questionEmbedding = await embedding_service.generate_embedding(request=EmbeddingText(text=message.content))
    
    try:
        relevant_contexts = embedding_service.qdrant_service.get_similar_vectors(questionEmbedding, top_k=5)
        print(f"Contexto recuperados: {relevant_contexts}")
    except Exception as e:
        print(f"No se pudieron recuperar contextos: {e}")
        relevant_contexts = []
    
    question = LlmQuestion(
            question=message.content,
            conversation=[msg["content"] for msg in context if msg["role"] != "system"],
            context=relevant_contexts
        )

    response_stream = llm_service.generate_response(question)

    def save_message_task(chat_id: int, content: str):
        with SessionLocal() as db_session:
            model_msg = Message(chat_id=chat_id, role="assistant", content=content)
            db_session.add(model_msg)
            db_session.commit()

    def stream_generator():
        full_response = []
        for chunk in response_stream:
            full_response.append(chunk)
            yield chunk
        
        final_response = "".join(full_response)
        background_tasks.add_task(save_message_task, chat_db.id, final_response)

    return StreamingResponse(stream_generator(), media_type="text/plain")
