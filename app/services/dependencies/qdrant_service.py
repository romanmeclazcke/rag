from fastapi import Depends
from dependencies.qdrant_client import get_qdrant_client
from qdrant_client import QdrantClient
from services.qdrant_service import QDrantService

def get_qdrant_service(client: QdrantClient = Depends(get_qdrant_client)):
    return QDrantService(client)