from qdrant_client import QdrantClient
from fastapi import Depends
import os

def get_qdrant_client() -> QdrantClient:
    """
    Devuelve una instancia inicializada del cliente de Qdrant.
    Si no se puede conectar, lanza una excepción.
    """
    try:
        client = QdrantClient(host=os.getenv("QDRANT_HOST"), port=os.getenv("QDRANT_PORT"))
        client.get_collections()
        return client
    except Exception as e:
        print(f"Error al conectar con Qdrant: {e}")
        raise RuntimeError("No se pudo conectar con Qdrant.")