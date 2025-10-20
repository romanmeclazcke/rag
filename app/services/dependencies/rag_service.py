from fastapi import Depends
from services.dependencies.llm_service import get_llm_service
from services.dependencies.qdrant_service import get_qdrant_service
from services.dependencies.embedding_service import get_embedding_service
from services.rag_service import RagService

def get_rag_service(
    llm_service=Depends(get_llm_service),
    qdrant_service=Depends(get_qdrant_service),
    embedding_service=Depends(get_embedding_service)
):
    return RagService(llm_service,qdrant_service,embedding_service)