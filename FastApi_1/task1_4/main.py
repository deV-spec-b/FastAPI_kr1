from fastapi import FastAPI
from task1_4.models import User

app=FastAPI()

user= User (name="Иван Скоробагатько", id=1)

@app.post("/users")
async def inf_user():
    return user

@app.post("/")
async def root():
    return {"message: Полная информация на /users"}