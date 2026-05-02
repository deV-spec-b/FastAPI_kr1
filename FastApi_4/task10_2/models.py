from pydantic import BaseModel, EmailStr, Field, conint, constr
from typing import Optional


class User(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    age: conint(gt=18, le=120)  # greater than 18, less than or equal 120
    email: EmailStr
    password: constr(min_length=8, max_length=16)
    phone: Optional[str] = 'Unknown'


class UserResponse(BaseModel):
    username: str
    age: int
    email: str
    phone: str