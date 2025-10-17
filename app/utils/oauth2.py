from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os 
import dependencies.database  as database
from schemas.token import TokenData

from model.user import User

load_dotenv()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_token(data: dict):
    copy = data.copy() # payload to encode into our token
    expire = datetime.now() + timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))) # type: ignore
    copy.update({"expiration": expire.isoformat()})

    token = jwt.encode(copy, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))  # type: ignore

    return token

def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")]) # type: ignore
        id: int = payload.get("user_id")  # type: ignore

        if not id:
            raise credentials_exception
        
        token_data = TokenData(id=id)
    except JWTError: 
        raise credentials_exception
    
    return token_data
    
def get_current_user(tokenUser: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated", headers={"WWW-Authenticate": "Bearer"})
    token: TokenData = verify_token(tokenUser, credentials_exception)

    user = db.query(User).filter(User.id == token.id).first()
    return user