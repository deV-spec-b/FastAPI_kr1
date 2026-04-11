from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

app = FastAPI()

security = HTTPBasic()

VALID_USERNAME = "admin"
VALID_PASSWORD = "12345"

def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    # Сравниваем логин (защита от тайминг-атак)
    correct_username = secrets.compare_digest(
        credentials.username,
        VALID_USERNAME
    )
    
    # Сравниваем пароль (защита от тайминг-атак)
    correct_password = secrets.compare_digest(
        credentials.password,
        VALID_PASSWORD
    )
    
    # Если хоть что-то не совпало
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},  
        )
    
    # Если всё правильно, возвращаем имя пользователя
    return credentials.username

@app.get("/secret")
async def get_secret(username: str = Depends(authenticate_user)):

    return {
        "message": f"You got my secret, welcome {username}!",
        "secret": "..."
    }