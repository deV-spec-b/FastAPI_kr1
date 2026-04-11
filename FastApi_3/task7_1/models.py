from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    user = "user"
    guest = "guest"

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=4)
    role: UserRole = Field(default=UserRole.user, description="Роль пользователя")

class UserLogin(BaseModel):
    username: str
    password: str

class UserInDB(BaseModel):
    username: str
    hashed_password: str
    role: UserRole

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class Item(BaseModel):
    id: int
    title: str
    description: str
    owner: str

class ItemCreate(BaseModel):
    title: str
    description: str

class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class MessageResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    detail: str