from pydantic import BaseModel, Field
from typing import Optional

class UserBase(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Имя пользователя от 3 до 50 символов",
        example="ivan"
    )

class User(UserBase):
    password: str = Field(
        ...,
        min_length=4,
        description="Пароль от 4 символов",
        example="qwerty"
    )

class UserInDB(UserBase):
    hashed_password: str = Field(
        ...,
        description="Хэш пароль(bcrypt)"
    )

class RegisterResponse(BaseModel):
    message: str = Field(
        ...,
        description="Успешная регистрация"
    )
    username: str = Field(
        ...,
        description="Имя зарегестрированного пользователя"
    )

class LoginResponse(BaseModel):
    message: str = Field(
        ...,
        description="Успешный вход"
    )

class ErrorResponse(BaseModel):
    message: str = Field(
        ...,
        description="Ошибка"
    )