from schemas.embedding import EmbeddingText
from services.qdrant_service import QDrantService
import io, os
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader
from llama_index.core.node_parser import SentenceSplitter
from docx import Document
from utils.hash import get_file_hash

class EmbeddingService:
    def __init__(self, qdrant_service: QDrantService):
        # Modelo eficiente y compatible con Qdrant (768 dimensiones)
        self.model = SentenceTransformer(os.getenv("EMBEDDING_MODEL"), trust_remote_code=True)
        self.qdrant_service = qdrant_service
        
    async def generate_embedding(self, request: EmbeddingText=None, file=None, save: bool = False):
        """Genera un embedding para texto/archivo dado usando Ollama. Si 'save' es True, guarda el embedding en Qdrant."""
        try:
            file_hash = None
            if file:
                content = file.file.read()
                if not content:
                    raise ValueError("El archivo está vacío.")

                file_hash = get_file_hash(content)
                if self.qdrant_service.check_if_hash_exists(file_hash):
                    raise ValueError("El archivo ya fue subido anteriormente.")
                
                text = self.extract_text_from_file(content, file.filename)
                if not text or text.strip() == "":
                    raise ValueError("El archivo está vacío o no contiene texto válido.")
            elif request and request.text:
                text = request.text
            else:
                raise ValueError("Debes proporcionar texto o un archivo válido.")
            
            chunks = self.chunk_text(text)
            print(f"Texto dividido en {len(chunks)} fragmentos")

             # Generar embeddings en batch (MUY rápido)
            embeddings = self.model.encode(chunks, show_progress_bar=True)

            if save:
                for chunk, emb in zip(chunks, embeddings):
                    self.qdrant_service.save_vector(chunk, emb, file_hash)

            return embeddings.tolist()
        except ValueError as e:
            # Re-lanzar ValueError para que el controlador lo atrape específicamente
            raise e
        except Exception as e:
            print(f"Error al generar embedding: {e}")
            raise RuntimeError("No se pudo generar el embedding.")    
    
    def extract_text_from_file(self, content: bytes, filename: str) -> str:
        """Extrae texto desde archivos TXT, PDF o DOCX."""
        filename = filename.lower()

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

    def chunk_text(self, text: str) -> list[str]:
        """Divide el texto en fragmentos (chunks) de manera automática y semánticamente coherente.
        Usa LlamaIndex para respetar párrafos, oraciones y mantener coherencia entre fragmentos."""

        splitter = SentenceSplitter(chunk_size=400, chunk_overlap=50)
        chunks = splitter.split_text(text)

        # Si solo hay un chunk pero el texto es largo, dividir manualmente
        if len(chunks) == 1 and len(text) > 600:
            chunks = [text[i:i+400] for i in range(0, len(text), 400)]

        return chunks
        
        

