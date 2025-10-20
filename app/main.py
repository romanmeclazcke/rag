from fastapi import FastAPI
from api.routes import embedding_controller, user_controller, message_controller, chat_controller, auth_controller
from services.qdrant_service import QDrantService
from dependencies.qdrant_client import get_qdrant_client
from model import Base
from dependencies.database import engine
from dotenv import load_dotenv
import os

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Qdrant RAG API")

@app.on_event("startup")
def on_startup():
    qdrantService = QDrantService(get_qdrant_client())
    qdrantService.create_collection_if_not_exists()
    

app.include_router(embedding_controller.router)
app.include_router(message_controller.router)
app.include_router(chat_controller.router)
app.include_router(user_controller.router)
app.include_router(auth_controller.router)

@app.get("/", tags=["health"])
def read_root():
    return {"message": "FastAPI application is running"}


