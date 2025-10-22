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

    def save_vector(self, text: str, vector: List[float], file_hash: str | None = None):
        """
        Guarda un vector en Qdrant asociado al texto dado.
        """
        payload = {"text": text}
        if file_hash:
            payload["file_hash"] = file_hash
            
        try:
            point = models.PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload=payload
            )
            self.client.upsert(
                collection_name=os.getenv("COLLECTION_NAME"),
                points=[point]
            )
        except Exception as e:
            print(f"Error al guardar el vector en Qdrant: {e}")
            raise RuntimeError("No se pudo guardar el vector en Qdrant.")

    def check_if_hash_exists(self, file_hash: str) -> bool:
        """
        Verifica si ya existe un punto con el hash de archivo dado en Qdrant.
        """
        try:
            search_result = self.client.scroll(
                collection_name=os.getenv("COLLECTION_NAME"),
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="file_hash",
                            match=models.MatchValue(value=file_hash),
                        )
                    ]
                ),
                limit=1,
            )
            return len(search_result[0]) > 0
        except Exception as e:
            print(f"Error al verificar el hash en Qdrant: {e}")
            # En caso de error, es más seguro asumir que no existe para permitir el flujo.
            return False
        
        
    def get_similar_vectors(self, query_vector: List[float], top_k: int = 3) -> List[str]:
        """
        Recupera los textos asociados a los vectores más similares en Qdrant.
        """
        try:
            if isinstance(query_vector, list) and len(query_vector) == 1 and isinstance(query_vector[0], list):
                query_vector = query_vector[0]

            search_result = self.client.search(
                collection_name=os.getenv("COLLECTION_NAME"),
                query_vector=query_vector,
                limit=top_k)

            relevant = [point.payload.get("text", "") for point in search_result if point.payload and point.score >= 0.45] # Establezco un umbral, para solo traer contenido realmente relacionado
            if not relevant:
                print("No se encontraron contextos relevantes")

            return relevant
        except Exception as e:
            print(f"Error al recuperar vectores similares de Qdrant: {e}")
            raise RuntimeError("No se pudieron recuperar vectores similares de Qdrant.")
