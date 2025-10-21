from qdrant_client import QdrantClient, models
import uuid
from typing import List
import os

class QDrantService:
    def __init__(self, client: QdrantClient):
        self.client = client

    def create_collection_if_not_exists(self):
        collections = self.client.get_collections()
        existing = [c.name for c in collections.collections]
        if os.getenv("COLLECTION_NAME") not in existing:
            print(f"Creando colección '{os.getenv('COLLECTION_NAME')}'...")
            self.client.recreate_collection(
                collection_name=os.getenv("COLLECTION_NAME"),
                vectors_config=models.VectorParams(
                    size=768, 
                    distance=models.Distance.COSINE
                )
            )

    def save_vector(self, text: str, vector: List[float]):
        """
        Guarda un vector en Qdrant asociado al texto dado.
        """
        try:
            point = models.PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={"text": text}
            )
            self.client.upsert(
                collection_name=os.getenv("COLLECTION_NAME"),
                points=[point]
            )
        except Exception as e:
            print(f"Error al guardar el vector en Qdrant: {e}")
            raise RuntimeError("No se pudo guardar el vector en Qdrant.")
        
        
    def get_similar_vectors(self, query_vector: List[float], top_k: int = 5) -> List[str]:
        """
        Recupera los textos asociados a los vectores más similares en Qdrant.
        """
        try:
            if query_vector and isinstance(query_vector[0], list):
                query_vector = query_vector[0]

            search_result = self.client.search(
                collection_name=os.getenv("COLLECTION_NAME"),
                query_vector=query_vector,
                limit=top_k
            )
            
            return [ point.payload.get("text", "") for point in search_result if point.payload is not None and point.score >= 0.70] # Establezco un umbral, para solo traer contenido realmente relacionado
        except Exception as e:
            print(f"Error al recuperar vectores similares de Qdrant: {e}")
            raise RuntimeError("No se pudieron recuperar vectores similares de Qdrant.")
