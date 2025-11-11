from sqlalchemy.orm import Session
from . import models,schemas
from .models import RoleEnum
from passlib.hash import argon2
from fastapi import HTTPException
from datetime import datetime,timedelta


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


def create_plan(db:Session,plan:schemas.PlanCreate):
    db_plan=models.Plan(
        name=plan.name,
        price=plan.price,
        features=plan.features,
        quota_limit=plan.quota_limit
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

def get_plans(db:Session):
    return db.query(models.Plan).all()

def get_plan_by_id(db:Session,plan_id:int):
    return db.query(models.Plan).filter(models.Plan.id==plan_id).first()

def update_plan(db:Session,plan_id:int,plan_update:schemas.PlanUpdate):
    db_plan=get_plan_by_id(db,plan_id)
    if not db_plan:
        return None
    update_data=plan_update.dict(exclude_unset=True)
    if not update_data:
        return None
    db.query(models.Plan).filter(models.Plan.id==plan_id).update(update_data)
    db.commit()
    return db.query(models.Plan).filter(models.Plan.id == plan_id).first()

def delete_plan(db: Session, plan_id: int):
    db_plan = get_plan_by_id(db, plan_id)
    if not db_plan:
        return None
    db.delete(db_plan)
    db.commit()
    return db_plan

def create_subscription(db:Session,user_id:int,plan_id:int):
    active_subs=db.query(models.Subscription).filter(models.Subscription.user_id==user_id,models.Subscription.status=="active").first()
    if active_subs:
        active_subs.status="inactive"
        db.add(active_subs)
    
    if active_subs and active_subs.plan_id==plan_id:
        raise HTTPException(status_code=403,detail="User already subscribed to this plan")
    
    db_sub=models.Subscription(
        user_id=user_id,
        plan_id=plan_id,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow()+timedelta(days=30),
        status="active"
        )
    db.add(db_sub)
    db.commit()
    db.refresh(db_sub)
    return db_sub

def get_user_subscriptions(db:Session,user_id:int):
    return db.query(models.Subscription).filter(models.Subscription.user_id==user_id).all()