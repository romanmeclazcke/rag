from typing import List
from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from schemas.user import UserCreate, UserResponse
from dependencies.database import get_db
from model.user import User
from utils.hash import hash


router = APIRouter(prefix="/users", 
                   tags=['Users']) 

@router.get("/", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.post("/", status_code = status.HTTP_201_CREATED, response_model=UserResponse) 
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_pwd = hash(user.password)
    user.password = hashed_pwd # update the model

    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"User with email {user.email} already exists")
    
    created_user = User(**user.model_dump()) 
    db.add(created_user)
    db.commit() 
    db.refresh(created_user) 

    return created_user 

@router.get("/{id}", response_model=UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} does not exist")
    
    return user

@router.delete("/{id}", status_code = status.HTTP_204_NO_CONTENT)
def delete_user(id: int, db: Session = Depends(get_db)):
    find_user = db.query(User).filter(User.id == id)
    if not find_user.first():
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"User with id {id} does not exist")
    
    find_user.delete(synchronize_session=False) # opción más eficiente
    db.commit()

    return Response(status_code = status.HTTP_204_NO_CONTENT)