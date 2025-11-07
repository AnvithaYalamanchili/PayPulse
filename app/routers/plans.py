from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from .. import schemas,crud
from ..database import get_db
from ..auth import verify_access_token
from ..models import User,RoleEnum
from fastapi.security import OAuth2PasswordBearer
from typing import List

router=APIRouter(
    prefix="/plans",
    tags=["plans"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.email == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.post("/",response_model=schemas.PlanOut)
def create_plan(plan:schemas.PlanCreate, db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    if current_user.role!=RoleEnum.admin:
        raise HTTPException(status_code=403,detail="Only admin can create plans")
    plan=crud.create_plan(db,plan)
    return plan

@router.get("/",response_model=List[schemas.PlanOut])
def list_plans(db:Session=Depends(get_db)):
    return crud.get_plans(db)

@router.put("/{plan_id}",response_model=schemas.PlanOut)
def update_plan(plan_id:int,plan_update:schemas.PlanUpdate,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    if current_user.role!=RoleEnum.admin:
        raise HTTPException(status_code=403,detail="Onlu admin can update the plan")
    updated=crud.update_plan(db,plan_id,plan_update)
    if not updated:
        raise HTTPException(status_code=404,detail="Plan not found")
    return updated

@router.delete("/{plan_id}")
def delete_plan(id:int,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    if current_user.role!=RoleEnum.admin:
        raise HTTPException(status_code=403,detail="Only admin can delete the plan")
    
    deleted=crud.delete_plan(db,id)
    if not deleted:
        raise HTTPException(status_code=404,detail="Plan not found")
    return {"message":"Plan deleted successfully"}