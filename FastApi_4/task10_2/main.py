from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from .models import User, UserResponse
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Задание 10.2 - Валидация данных и обработка ошибок")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")

    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "error_type": error["type"],
            "input_value": error.get("input", None)
        })

    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": errors,
            "path": request.url.path,
            "timestamp": datetime.now().isoformat()
        }
    )


users_db = {}


@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user: User):
    if user.username in users_db:
        raise HTTPException(
            status_code=409,
            detail=f"User with username '{user.username}' already exists"
        )

    users_db[user.username] = user

    return UserResponse(
        username=user.username,
        age=user.age,
        email=user.email,
        phone=user.phone
    )


@app.get("/users/{username}", response_model=UserResponse)
async def get_user(username: str):
    if username not in users_db:
        raise HTTPException(
            status_code=404,
            detail=f"User with username '{username}' not found"
        )

    user = users_db[username]
    return UserResponse(
        username=user.username,
        age=user.age,
        email=user.email,
        phone=user.phone
    )


@app.get("/")
async def root():
    return {
        "task": "10.2",
        "title": "Валидация данных и обработка ошибок",
        "validation_rules": {
            "username": "от 3 до 50 символов",
            "age": "больше 18 и не больше 120",
            "email": "валидный email",
            "password": "от 8 до 16 символов",
            "phone": "опционально, по умолчанию 'Unknown'"
        },
        "example": {
            "username": "john_doe",
            "age": 25,
            "email": "john@example.com",
            "password": "secret12345"
        }
    }