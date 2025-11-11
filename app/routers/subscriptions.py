from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session  
from .. import schemas,crud
from ..database import get_db   
from ..auth import verify_access_token  
from ..models import User
from fastapi.security import OAuth2PasswordBearer
from typing import List

router=APIRouter(
    prefix="/subscriptions",
    tags=["subscriptions"]
)

oauth2_scheme=OAuth2PasswordBearer("/users/login")

def get_current_user(token:str=Depends(oauth2_scheme),db:Session=Depends(get_db)):
    payload=verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401,detail="Invalid access token")
    user=db.query(User).filter(User.email==payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    return user

@router.post('/',response_model=schemas.SubscriptionOut)
def subscribe(subscription:schemas.SubscriptionCreate,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    try:
        sub=crud.create_subscription(db,user_id=current_user.id,plan_id=subscription.plan_id)
        return sub
    except Exception as e:
        raise HTTPException(status_code=400,detail=str(e))
    
@router.get('/me',response_model=List[schemas.SubscriptionOut])
def get_my_subscriptions(db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    my_subs=crud.get_user_subscriptions(db,current_user.id)
    return my_subs
