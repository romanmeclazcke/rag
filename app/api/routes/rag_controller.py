from fastapi import APIRouter
from fastapi import status
from schemas.llm import UserQuestion
from services.rag_service import RagService
from services.dependencies.rag_service import get_rag_service
from fastapi import Depends

router = APIRouter()


@router.post("/query", status_code=status.HTTP_200_OK)
def rag_query(
    userQuestion: UserQuestion,
    service: RagService = Depends(get_rag_service)):
    ansawer = service.answer_question(userQuestion)
    return {"answer": ansawer}
    
