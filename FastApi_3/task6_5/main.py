import os
import jwt
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .models import UserRegister, TokenResponse, UserResponse, ErrorResponse

SECRET_KEY = "my-super-secret-jwt-key-2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
users_db: Dict[str, Dict] = {}

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(username: str) -> str:
    payload = {
        "sub": username,  # subject — идентификатор пользователя
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.now(timezone.utc)  # issued at — время создания
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def get_user(username: str) -> Optional[Dict]:
    return users_db.get(username)


def authenticate_user(username: str, password: str) -> bool:
    user = get_user(username)
    if not user:
        return False
    
    # secrets.compare_digest() защищает от тайминг-атак
    if not verify_password(password, user["hashed_password"]):
        return False
    
    return True


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username = verify_access_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return username

app = FastAPI()

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        429: {"model": ErrorResponse}
    }
)
@limiter.limit("1/minute") 
async def register(request: Request, user_data: UserRegister):
    if user_data.username in users_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )

    hashed_password = get_password_hash(user_data.password)

    users_db[user_data.username] = {
        "username": user_data.username,
        "hashed_password": hashed_password
    }
    
    return UserResponse(
        username=user_data.username,
        message="User created successfully"
    )

@app.post(
    "/login",
    response_model=TokenResponse,
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        429: {"model": ErrorResponse}
    }
)
@limiter.limit("5/minute") 
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    

    access_token = create_access_token(form_data.username)
    
    return TokenResponse(access_token=access_token, token_type="bearer")

@app.get(
    "/protected_resource",
    response_model=UserResponse,
    responses={
        401: {"model": ErrorResponse}
    }
)
async def protected_resource(current_user: str = Depends(get_current_user)):
    return UserResponse(
        username=current_user,
        message=f"You have accessed a protected resource! Welcome, {current_user}!"
    )