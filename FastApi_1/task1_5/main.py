from fastapi import FastAPI
from task1_5.models import User

app = FastAPI()

user= User (name="Иван Скоробагатько", age=19)

@app.get("/")
async def root():
    return {"message": "Отправьте POST запрос на /user с именем и возрастом"}

@app.post("/user") 
async def check_user(user_data: User):  

    is_adult = user_data.age >= 18
    
    return {
        "name": user_data.name,
        "age": user_data.age,
        "is_adult": is_adult
    }