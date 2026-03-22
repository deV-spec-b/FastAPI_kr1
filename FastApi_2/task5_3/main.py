from fastapi import FastAPI, Response, Request, HTTPException, status, Form, Cookie
import uuid
import time
from typing import Optional, Dict, Any
from itsdangerous import URLSafeSerializer, BadSignature, SignatureExpired
from datetime import datetime

app = FastAPI()

SECRET_KEY = "my-super-secret-key-2026-mirea-dynamic"

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

last_activity_store: Dict[str, float] = {}

def create_session_token(user_id: str, timestamp: Optional[float] = None) -> str:
    if timestamp is None:
        timestamp = time.time()
    
    data = {
        "user_id": user_id,
        "timestamp": timestamp
    }
    
    return serializer.dumps(data)

def verify_session_token(token: str) -> Optional[Dict[str, Any]]:
    
    try:
        data = serializer.loads(token)
        
        if "user_id" not in data or "timestamp" not in data:
            return None
            
        return data
    except BadSignature:
        return None

@app.post("/login", status_code=status.HTTP_200_OK)
async def login(
    response: Response,
    username: str = Form(..., description="Имя пользователя"),
    password: str = Form(..., description="Пароль")
):
    if username not in USERS_DB:
        raise HTTPException(status_code=401, detail="Неверные данные")
    
    if USERS_DB[username]["password"] != password:
        raise HTTPException(status_code=401, detail="Неверные данные")
    
    user_id = USERS_DB[username]["user_id"]
    
    current_time = time.time()
    session_token = create_session_token(user_id, current_time)
    
    last_activity_store[user_id] = current_time
    
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        max_age=300, 
        path="/",
        samesite="lax"
    )
    
    return {
        "message": "Успешный вход",
        "username": username,
        "user_id": user_id,
        "login_time": datetime.fromtimestamp(current_time).strftime("%H:%M:%S"),
        "session_expires_in": "5 минут",
        "token_data": {
            "user_id": user_id,
            "timestamp": current_time
        }
    }

@app.get("/profile")
async def get_profile(
    request: Request,
    response: Response,
    session_token: Optional[str] = Cookie(None)
):
    if not session_token:
        response.status_code = 401
        return {"message": "Unauthorized - отсутствует session_token"}
    
    token_data = verify_session_token(session_token)
    
    if not token_data:
        response.status_code = 401
        return {
            "message": "Invalid session - подпись недействительна",
            "hint": "itsdangerous обнаружил подделку данных"
        }
    
    user_id = token_data["user_id"]
    token_time = token_data["timestamp"]
    current_time = time.time()
    time_diff = current_time - token_time
    
    if user_id not in USER_ID_INDEX:
        response.status_code = 401
        return {"message": "Unauthorized - пользователь не найден"}
    
    username = USER_ID_INDEX[user_id]
    user_data = USERS_DB[username]
    
    session_extended = False
    new_token = None
    
    if time_diff >= 300: 
        response.status_code = 401
        return {
            "message": "Session expired",
            "details": f"Прошло {time_diff:.1f} секунд (> 5 минут)",
            "last_activity": datetime.fromtimestamp(token_time).strftime("%H:%M:%S"),
            "current_time": datetime.fromtimestamp(current_time).strftime("%H:%M:%S")
        }
    
    if time_diff >= 180: 
        new_token = create_session_token(user_id, current_time)
        last_activity_store[user_id] = current_time
        session_extended = True
        
        response.set_cookie(
            key="session_token",
            value=new_token,
            httponly=True,
            max_age=300,
            path="/"
        )
    
    profile_data = {
        "username": username,
        "name": user_data["name"],
        "email": user_data["email"],
        "user_id": user_id,
        "session_status": {
            "time_elapsed": f"{time_diff:.1f} секунд",
            "time_elapsed_minutes": f"{time_diff/60:.1f} минут",
            "last_activity": datetime.fromtimestamp(token_time).strftime("%H:%M:%S"),
            "current_time": datetime.fromtimestamp(current_time).strftime("%H:%M:%S")
        },
        "message": f"Добро пожаловать, {user_data['name']}!"
    }
    
    if session_extended:
        profile_data["session_extended"] = True
        profile_data["new_expires_in"] = "5 минут с текущего момента"
        profile_data["new_token"] = new_token  
    
    return profile_data

@app.get("/debug/session-info")
async def get_session_info(request: Request):

    session_token = request.cookies.get("session_token")
    
    if not session_token:
        return {"message": "Нет активной сессии"}
    
    token_data = verify_session_token(session_token)
    
    if not token_data:
        return {
            "token": session_token[:20] + "...",
            "valid": False,
            "message": "Недействительная подпись"
        }
    
    current_time = time.time()
    time_diff = current_time - token_data["timestamp"]
    
    return {
        "token_valid": True,
        "user_id": token_data["user_id"],
        "timestamp": token_data["timestamp"],
        "timestamp_readable": datetime.fromtimestamp(token_data["timestamp"]).strftime("%H:%M:%S"),
        "current_time": datetime.fromtimestamp(current_time).strftime("%H:%M:%S"),
        "time_elapsed": f"{time_diff:.1f} секунд",
        "time_elapsed_minutes": f"{time_diff/60:.1f} минут",
        "session_status": "активна" if time_diff < 300 else "истекла",
        "will_extend": "да" if 180 <= time_diff < 300 else "нет" if time_diff < 180 else "истекла"
    }

@app.post("/logout")
async def logout(response: Response):
    """Выход из системы"""
    response.delete_cookie("session_token")
    return {"message": "Выход выполнен успешно"}

@app.get("/")
async def root():
    return {
            "POST /login": "Вход (устанавливает cookie с timestamp)",
            "GET /profile": "Профиль с динамическим продлением",
            "GET /debug/session-info": "Информация о сессии",
            "POST /logout": "Выход"
    }