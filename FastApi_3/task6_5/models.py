from pydantic import BaseModel, Field
from typing import Optional

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=30, description="Имя пользователя")
    password: str = Field(..., min_length=8, description="Пароль - минимум 8 символов")

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    username: str
    message: str

class ErrorResponse(BaseModel):
    detail: str