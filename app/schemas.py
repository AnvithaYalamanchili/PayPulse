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
