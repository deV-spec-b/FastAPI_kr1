from fastapi import FastAPI, Response, Request, HTTPException, status, Form
from task3_2.models import LoginData
from typing import Optional
import uuid

app = FastAPI()

users_db = {
    "user123": {
        "password": "password123",
        "name": "Firstname Lastname",
        "email": "email@mail.ru"
    },
    "ivan": {
        "password": "12345",
        "name": "Иван Скоробагатько",
        "email": "ivan@mail.ru"
    },
    "admin": {
        "password": "admin123",
        "name": "Администратор",
        "email": "admin@mail.ru"
    }
}

active_sessions = {}

@app.post("/login", status_code=status.HTTP_200_OK)
async def login(
    response: Response,
    username: str = Form(..., description="Имя пользователя"),
    password: str = Form(..., description="Пароль")
):
    if username not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя или пароль"
        )
    
    if users_db[username]["password"] != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя или пароль"
        )
    
    session_token = str(uuid.uuid4())
    
    active_sessions[session_token]=username

    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        max_age=3600,
        path="/",
        samesite="lax"
    )

    return {
        "message": "Успешный вход",
        "username": username,
        "session_token": session_token
    }

@app.get("/user")
async def get_user_profile(request: Request, response: Response):
    session_token = request.cookies.get("session_token")

    if not session_token:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message: Unauthorized - отсутствует session_token"}
    if session_token not in active_sessions:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message: Unauthorized - недействительная сессия"}
    
    username = active_sessions[session_token]
    user_data = users_db[username]

    return {
        "username": username,
        "name": user_data["name"],
        "email": user_data["email"],
        "message": f"Добро пожаловать, {user_data['name']}!"
    }

@app.post("/logout")
async def logout(response: Response, request: Request):

    session_token = request.cookies.get("session_token")

    if session_token and session_token in active_sessions:
        del active_sessions[session_token]

    response.delete_cookie("session_token")

    return {"message": "Выход выполнен успешно"}

@app.get("/sessions")
async def get_active_sessions():
    sessions_info = {}
    for token, username in active_sessions.items():
        sessions_info[token[:8] + "..."]  = username

    return {
        "active_sessions_count": len(active_sessions),
        "sessions": sessions_info
    } 

@app.get("/")
async def root():
    return {
        "POST /login": "Вход (form-data: username, password) - устанавливает cookie",
        "GET /user": "Защищенный профиль (требуется cookie)",
        "POST /logout": "Выход - удаляет cookie",
        "GET /sessions": "[Отладка] Активные сессии"
    }
