from ollama import Client
from schemas.embedding import EmbeddingText
from services.qdrant_service import QDrantService
from ollama._types import EmbeddingsResponse 
import io
from PyPDF2 import PdfReader
from docx import Document

class EmbeddingService:
    def __init__(self, ollama_client: Client,qdrant_service:QDrantService):
        self.ollama_client = ollama_client
        self.qdrant_service = qdrant_service

    def generate_and_save_embedding(self, request: EmbeddingText):
        """
        Genera un embedding para el texto dado usando Ollama.
        """
        try:
            response:EmbeddingsResponse = self.ollama_client.embeddings(
                model="nomic-embed-text",
                prompt=request.text
            )
            
            self.qdrant_service.save_vector(request.text, list(response.embedding))
            return list(response.embedding)
        except Exception as e:
            print(f"Error al generar embedding: {e}")
            raise RuntimeError("No se pudo generar el embedding.")
        
    def generate_embedding(self, request: EmbeddingText):
        """
        Genera un embedding para el texto dado usando Ollama.
        """
        try:
            response:EmbeddingsResponse = self.ollama_client.embeddings(
                model="nomic-embed-text",
                prompt=request.text
            )
            
            return list(response.embedding)
        except Exception as e:
            print(f"Error al generar embedding: {e}")
            raise RuntimeError("No se pudo generar el embedding.")    
        
        
    async def generate_embedding_from_file(self, file):
        """
        Extrae texto desde un archivo y genera embeddings.
        """
        text = self._extract_text_from_file(file)
        if not text or text.strip() == "":
            raise ValueError("El archivo está vacío o no contiene texto válido.")

        return self.generate_and_save_embedding(EmbeddingText(text=text))

    def _extract_text_from_file(self, file) -> str:
        """
        Extrae texto desde archivos TXT, PDF o DOCX.
        """
        content = file.file.read()
        file.file.seek(0)  # resetea el puntero

        filename = file.filename.lower()

        if filename.endswith(".txt"):
            return content.decode("utf-8")

        elif filename.endswith(".pdf"):
            reader = PdfReader(io.BytesIO(content))
            return " ".join(page.extract_text() or "" for page in reader.pages)

        elif filename.endswith(".docx"):
            doc = Document(io.BytesIO(content))
            return " ".join(p.text for p in doc.paragraphs)

        else:
            raise ValueError("Formato de archivo no soportado (solo .txt, .pdf, .docx).")    