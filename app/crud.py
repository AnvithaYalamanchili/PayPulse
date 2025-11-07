from sqlalchemy.orm import Session
from . import models,schemas
from .models import RoleEnum
from passlib.hash import argon2
from fastapi import HTTPException as HTTP


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = argon2.hash(user.password)
    if user.role==RoleEnum.admin:
        existing_admin=db.query(models.User).filter(models.User.role==RoleEnum.admin).first()
        if existing_admin:
            raise HTTP(status_code=400,detail="An admin user already exists.")


    db_user = models.User(
        name=user.name,
        email=user.email,
        role=user.role,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db:Session,email:str):
    user=db.query(models.User).filter(models.User.email==email).first()
    return user

def authenticate_user(db:Session,email:str,password:str):
    user=db.query(models.User).filter(models.User.email==email).first()
    if not user:
        return None
    if not argon2.verify(password,user.password_hash):
        return None
    return user
