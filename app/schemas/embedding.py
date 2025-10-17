from pydantic import BaseModel

class EmbeddingText(BaseModel):
    text: str
