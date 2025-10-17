# services/embedding_service.py
from fastapi import Depends
from dependencies.ollama_client import get_ollama_client
from ollama import Client
from schemas.embedding import EmbeddingText
from services.embedding_service import EmbeddingService
from services.dependencies.qdrant_service import get_qdrant_service

def get_embedding_service(
    ollama_client: Client = Depends(get_ollama_client),
    qdrant_service = Depends(get_qdrant_service)
):
    """
    Devuelve una instancia de EmbeddingService con el cliente de Ollama inyectado.
    """
    return EmbeddingService(ollama_client,qdrant_service)