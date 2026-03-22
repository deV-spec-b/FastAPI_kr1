from fastapi import FastAPI
from .models import UserCreate

app = FastAPI()

@app.post("/user")
async def create_user(user: UserCreate):
    is_adult = user.age >= 0 if user.age else False
    
    return {
        "name": user.name,
        "email": user.email,
        "age": user.age,
        "is_subscribed": user.is_subscribed,
        "is_adult": is_adult
    }

@app.get("/")
async def root():
    return {
        "POST /user": "создать пользователя",
        "GET /docs": "документация Swagger"
        }