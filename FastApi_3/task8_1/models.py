from pydantic import BaseModel, Field
from typing import Optional

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, description="Имя пользователя")
    password: str = Field(..., min_length=4, description="Пароль")


class UserResponse(BaseModel):
    message: str
    username: str


class UserInDB(BaseModel):
    id: int
    username: str
    password: str


class ErrorResponse(BaseModel):
    detail: str