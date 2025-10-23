from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, status, Body
from services.embedding_service import EmbeddingService
from schemas.embedding import EmbeddingText
from services.dependencies.embedding_service import get_embedding_service

router = APIRouter(prefix="/embeddings", tags=["embeddings"])

@router.post("/upload/text", status_code=status.HTTP_200_OK)
async def upload_text(
    text: EmbeddingText,
    service: EmbeddingService = Depends(get_embedding_service)
):
    await service.generate_embedding(request=text, save=True)
    return {"message": "Embedding generado correctamente desde texto"}


@router.post("/upload/file", status_code=status.HTTP_200_OK)
async def upload_file(
    file: UploadFile = File(...),
    service: EmbeddingService = Depends(get_embedding_service)
):
    try:
        await service.generate_embedding(file=file, save=True)
        return {"message": f"Embedding generado correctamente desde archivo '{file.filename}'"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
