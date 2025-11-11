from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: Optional[str] 

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    role:str
    plan_id: Optional[int]
    created_at: datetime

    class Config:
        orm_mode = True


class PlanBase(BaseModel):
    name:str
    price:float
    features:str
    quota_limit:int

class PlanCreate(PlanBase):
    pass

class PlanUpdate(BaseModel):
    name:Optional[str]=None
    price:Optional[float]=None
    features:Optional[str]=None
    quota_limit:Optional[int]=None

class PlanOut(PlanBase):
    id:int
    created_at:datetime

    class Config:
        orm_mode = True

class SubscriptionCreate(BaseModel):
    plan_id:int

class SubscriptionOut(BaseModel):
    id:int
    user_id:int
    plan_id:int
    start_date:datetime
    end_date:datetime
    status:str
    payment_id:Optional[str]

    class Config:
        orm_mode:True