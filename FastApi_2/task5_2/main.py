from fastapi import FastAPI, Response, Request, HTTPException, status, Form, Cookie
import uuid
from typing import Optional, Dict
from itsdangerous import URLSafeSerializer, BadSignature, SignatureExpired
from datetime import datetime, timedelta

app = FastAPI()

SECRET_KEY = "my-super-secret-key-2026-mirea"

serializer = URLSafeSerializer(SECRET_KEY)

USERS_DB: Dict[str, Dict] = {
    "user123": {
        "user_id": str(uuid.uuid4()),
        "username": "user123",
        "password": "password123",
        "name": "Иван Петров",
        "email": "ivan@mail.ru"
    },
    "alice": {
        "user_id": str(uuid.uuid4()),
        "username": "alice",
        "password": "alicepass",
        "name": "Алиса Смирнова",
        "email": "alice@mail.ru"
    }
}

USER_ID_INDEX = {data["user_id"]: data["username"] for data in USERS_DB.values()}

@app.post("/login", status_code=status.HTTP_200_OK)
async def login(
    response: Response,
    username: str = Form(..., description="Имя пользователя"),
    password: str = Form(..., description="Пароль")
):
    if username not in USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль"
        )

    if USERS_DB[username]["password"] != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль"
        )

    user_id = USERS_DB[username]["user_id"]

    signed_token = serializer.dumps({"user_id": user_id})

    response.set_cookie(
        key="session_token",
        value=signed_token,
        httponly=True,
        max_age=3600,
        path="/",
        samesite="lax"
    )
    
    return {
        "message": "Успешный вход",
        "username": username,
        "user_id": user_id,
        "signed_token": signed_token, 
        "itsdangerous": "Библиотека автоматически создала подпись"
    }

@app.get("/profile")
async def get_profile(
    request: Request,
    response: Response,
    session_token: Optional[str] = Cookie(None, description="Подписанный токен сессии")
):
    if not session_token:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Unauthorized - отсутствует session_token"}
    
    try:
        data = serializer.loads(session_token)
        user_id = data.get("user_id")
        
    except BadSignature:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            "message": "Invalid session - подпись недействительна",
            "details": "BadSignature: данные были изменены после подписания",
            "hint": "itsdangerous обнаружил подделку cookie"
        }
    except Exception as e:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": f"Invalid session - {str(e)}"}
    
    if user_id not in USER_ID_INDEX:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Unauthorized - пользователь не найден"}
    
    username = USER_ID_INDEX[user_id]
    user_data = USERS_DB[username]
    
    return {
        "username": username,
        "name": user_data["name"],
        "email": user_data["email"],
        "user_id": user_id,
        "message": f"Добро пожаловать, {user_data['name']}! Подпись проверена itsdangerous",
        "verification_method": "itsdangerous автоматически проверил целостность данных"
    }

@app.get("/debug/token/{token}")
async def debug_token(token: str):

    try:
        data = serializer.loads(token)
        return {
            "token": token,
            "valid": True,
            "data": data,
            "message": "Подпись верна! Данные не были изменены"
        }
    except BadSignature:
        return {
            "token": token,
            "valid": False,
            "message": "BadSignature - подпись недействительна! Данные были изменены"
        }
    except Exception as e:
        return {
            "token": token,
            "valid": False,
            "error": str(e)
        }

@app.get("/debug/generate/{user_id}")
async def debug_generate(user_id: str):

    token = serializer.dumps({"user_id": user_id})
    
    return {
        "user_id": user_id,
        "token": token,
        "format": "itsdangerous автоматически добавил подпись"
    }

@app.post("/logout")
async def logout(response: Response):
    """Выход из системы"""
    response.delete_cookie("session_token")
    return {"message": "Выход выполнен успешно"}

@app.get("/")
async def root():
    return {
            "POST /login": "Вход (использует itsdangerous.dumps)",
            "GET /profile": "Профиль (использует itsdangerous.loads)",
            "GET /debug/token/{token}": "Проверить любой токен",
            "GET /debug/generate/{user_id}": "Сгенерировать токен"
    }