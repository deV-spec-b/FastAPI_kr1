from pydantic import BaseModel, Field
from typing import Optional

class LoginRequest(BaseModel):
    username: str = Field(..., description="Имя пользователя")
    password: str = Field(..., description="Пароль")

class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT-токен")

class ProtectedResponse(BaseModel):
    message: str = Field(..., description="Сообщение об успешном входе")
    user: str = Field(..., description="Имя пользователя токена")

class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Ошибка")