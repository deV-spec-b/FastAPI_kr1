import jwt
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from .models import TokenResponse, ProtectedResponse, ErrorResponse


SECRET_KEY = "my-super-secret-jwt-key-2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


fake_users_db: Dict[str, str] = {
    "ivan": "12345",
    "bob": "bob456",
    "admin": "admin123"
}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(username: str) -> str:
    payload = {
        "sub": username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        return username
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def get_user(username: str) -> Optional[Dict]:
    if username in fake_users_db:
        return {"username": username, "password": fake_users_db[username]}
    return None


def authenticate_user(username: str, password: str) -> bool:
    user = get_user(username)
    if not user:
        return False
    return secrets.compare_digest(user["password"], password)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    username = verify_access_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return username


app = FastAPI()


@app.post(
    "/login",
    response_model=TokenResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Неверные учетные данные"}
    }
)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if not authenticate_user(form_data.username, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(form_data.username)
    return TokenResponse(access_token=access_token, token_type="bearer")


@app.get(
    "/protected_resource",
    response_model=ProtectedResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Невалидный или отсутствующий токен"}
    }
)
async def protected_resource(current_user: str = Depends(get_current_user)):
    return ProtectedResponse(
        message="You have accessed a protected resource!",
        user=current_user
    )
