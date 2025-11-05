from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import crud, schemas, database, models
from fastapi.security import OAuth2PasswordRequestForm
from ..auth import create_access_token  
from ..database import get_db

router=APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/signup",response_model=schemas.UserResponse)
def signup(user:schemas.UserCreate,db:Session=Depends(get_db)):
    db_user=crud.get_user_by_email(db,user.email)
    if db_user:
        raise HTTPException(status_code=400,detail=f"User with email {user.email} already exists")
    user=crud.create_user(db,user)
    return user

@router.post("/login")
def login(form_data:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    email=form_data.username
    password=form_data.password
    user=crud.authenticate_user(db,email,password)
    if not user:
        raise HTTPException(status_code=401,detail="Invalid email or password")
    access_token=create_access_token(data={"sub":user.email})
    return {"access_token":access_token,"token_type":"bearer"}


