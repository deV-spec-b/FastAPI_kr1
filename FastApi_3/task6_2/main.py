from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
import secrets
from typing import Dict, Optional

from .models import User, UserInDB, RegisterResponse, LoginResponse, ErrorResponse

app = FastAPI()

security = HTTPBasic()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

users_db: Dict[str, UserInDB] = {}

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_user(username: str) -> Optional[UserInDB]:
    return users_db.get(username)

@app.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"model": ErrorResponse, "description": "Пользователь уже существует"},
        400: {"model": ErrorResponse, "description": "Некорректные данные"}
    },
    summary="Регистрация нового пользователя"
)
async def register(user: User):
    if user.username in users_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )
    
    hashed_password = get_password_hash(user.password)
    
    user_in_db = UserInDB(
        username=user.username,
        hashed_password=hashed_password
    )
    
    users_db[user.username] = user_in_db
    
    return RegisterResponse(
        message="User registered successfully!",
        username=user.username
    )

def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    user = get_user(credentials.username)
    
    username_matches = secrets.compare_digest(
        credentials.username,
        user.username if user else ""
    )
    
    if not user or not username_matches:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return user.username

@app.get(
    "/login",
    response_model=LoginResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Неверные учетные данные"}
    },
    summary="Вход в систему"
)
async def login(username: str = Depends(authenticate_user)):
    return LoginResponse(message=f"Welcome, {username}!")
