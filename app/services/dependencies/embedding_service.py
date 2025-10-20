# services/embedding_service.py
from fastapi import Depends
from services.embedding_service import EmbeddingService
from services.dependencies.qdrant_service import get_qdrant_service

def get_embedding_service(
    qdrant_service = Depends(get_qdrant_service)
):
    """
    Devuelve una instancia de EmbeddingService.
    """
    return EmbeddingService(qdrant_service)