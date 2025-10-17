from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from dependencies.database import get_db
from schemas.token import Token
from model.user import User
from utils.hash import verify
from utils import oauth2

router = APIRouter(tags=['Authentication'])

@router.post("/login", response_model=Token)
def login(credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)): # espera las credenciales en form-data, no raw
    user = db.query(User).filter(User.email == credentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")
    
    if not verify(credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")
    
    token = oauth2.create_token(data = {"user_id": user.id}) # a elección y opcional; qué enviar en el payload
    return {"token": token, "type": "bearer"}