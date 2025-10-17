from fastapi import APIRouter, HTTPException
from services.embedding_service import EmbeddingService
from schemas.embedding import EmbeddingText
from fastapi import status
from services.dependencies.embedding_service import get_embedding_service
from fastapi import UploadFile, File


router = APIRouter()


from fastapi import APIRouter, Depends


@router.post("/embed/text", status_code=status.HTTP_200_OK)
def create_embedding(
    request_body: EmbeddingText,
    service: EmbeddingService = Depends(get_embedding_service)
):
    try:
        service.generate_and_save_embedding(request_body)
        return {"message": "Embedding generado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  



@router.post("/embed/file", status_code=status.HTTP_200_OK)
async def create_embedding_from_file(
    file: UploadFile = File(...),
    service: EmbeddingService = Depends(get_embedding_service),
):
    """
    Genera embeddings desde un archivo (txt, pdf, docx).
    """
    try:
        await service.generate_embedding_from_file(file)
        return {"message": f" Embedding generado correctamente desde archivo '{file.filename}'"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))