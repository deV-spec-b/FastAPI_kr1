import jwt
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, List
from enum import Enum

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext

from pydantic import BaseModel, Field
from .models import UserRole, UserRegister, UserLogin, UserInDB, TokenResponse, Item, ItemCreate, ItemUpdate, MessageResponse, ErrorResponse

SECRET_KEY = "my-super-secret-jwt-key-2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

users_db: Dict[str, UserInDB] = {}
items_db: Dict[int, Item] = {}
next_item_id = 1

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(username: str, role: UserRole) -> str:
    payload = {
        "sub": username,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(token: str) -> Optional[tuple]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")
        if username is None or role is None:
            return None
        return (username, role)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def get_user(username: str) -> Optional[UserInDB]:
    return users_db.get(username)


def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)) -> tuple:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    result = verify_access_token(token)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return result


def require_role(allowed_roles: List[UserRole]):
    async def role_checker(user_data: tuple = Depends(get_current_user)):
        username, role = user_data
        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in allowed_roles]}, your role: {role.value}"
            )
        return user_data
    return role_checker


require_admin = require_role([UserRole.ADMIN])
require_user_or_admin = require_role([UserRole.USER, UserRole.ADMIN])
require_any = require_role([UserRole.ADMIN, UserRole.USER, UserRole.GUEST])


app = FastAPI(
    title="Задание 7.1 - RBAC",
    description="Role-Based Access Control",
    version="1.0.0"
)


@app.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    if user_data.username in users_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    
    hashed_password = get_password_hash(user_data.password)
    user_in_db = UserInDB(
        username=user_data.username,
        hashed_password=hashed_password,
        role=user_data.role
    )
    users_db[user_data.username] = user_in_db
    return MessageResponse(message=f"User {user_data.username} created with role {user_data.role.value}")


@app.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(user.username, user.role)
    return TokenResponse(access_token=access_token, token_type="bearer")


@app.get("/items", response_model=List[Item])
async def get_all_items(user_data: tuple = Depends(require_any)):
    return list(items_db.values())


@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int, user_data: tuple = Depends(require_any)):
    if item_id not in items_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return items_db[item_id]


@app.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item_data: ItemCreate, user_data: tuple = Depends(require_user_or_admin)):
    global next_item_id
    username, role = user_data
    new_item = Item(
        id=next_item_id,
        title=item_data.title,
        description=item_data.description,
        owner=username
    )
    items_db[next_item_id] = new_item
    next_item_id += 1
    return new_item


@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item_data: ItemUpdate, user_data: tuple = Depends(require_user_or_admin)):
    username, role = user_data
    if item_id not in items_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    item = items_db[item_id]
    if role != UserRole.ADMIN and item.owner != username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own items"
        )
    
    if item_data.title is not None:
        item.title = item_data.title
    if item_data.description is not None:
        item.description = item_data.description
    
    items_db[item_id] = item
    return item


@app.delete("/items/{item_id}", response_model=MessageResponse)
async def delete_item(item_id: int, user_data: tuple = Depends(require_admin)):
    if item_id not in items_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    del items_db[item_id]
    return MessageResponse(message=f"Item {item_id} deleted successfully")


@app.get("/admin-only", response_model=MessageResponse)
async def admin_only_endpoint(user_data: tuple = Depends(require_admin)):
    username, role = user_data
    return MessageResponse(message=f"Hello, admin {username}! This is admin-only endpoint.")


@app.get("/user-area", response_model=MessageResponse)
async def user_area_endpoint(user_data: tuple = Depends(require_user_or_admin)):
    username, role = user_data
    return MessageResponse(message=f"Welcome, {username}! Your role is {role.value}.")


@app.get("/whoami", response_model=dict)
async def whoami(user_data: tuple = Depends(require_any)):
    username, role = user_data
    return {
        "username": username,
        "role": role.value,
        "message": f"You are logged in as {username} with role {role.value}"
    }
