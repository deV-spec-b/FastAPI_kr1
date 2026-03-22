from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Number(BaseModel):
    num1: float
    num2: float

@app.post("/calc")
async def root(number: Number):
    result = number.num1 + number.num2
    return {"result": result}