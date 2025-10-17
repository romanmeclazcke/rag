from fastapi import FastAPI
from api.routes import embedding_controller
from services.qdrant_service import QDrantService
from dependencies.qdrant_client import get_qdrant_client
from api.routes import rag_controller
from model import Base
from dependencies.database import engine


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Qdrant RAG API")

@app.on_event("startup")
def on_startup():
    qdrantService = QDrantService(get_qdrant_client())
    qdrantService.create_collection_if_not_exists()
    

app.include_router(embedding_controller.router, prefix="/api/embeddings", tags=["embeddings"])
app.include_router(rag_controller.router, prefix="/api/rag", tags=["rag"])




@app.get("/", tags=["health"])
def read_root():
    return {"message": "FastAPI application is running"}


