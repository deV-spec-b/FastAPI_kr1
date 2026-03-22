from fastapi import FastAPI, Depends, Response, HTTPException, status
from datetime import datetime
from typing import Optional
from .models import CommonHeaders

app = FastAPI()

async def get_common_headers(
    headers: CommonHeaders = Depends()
) -> CommonHeaders:
    return headers

@app.get("/headers")
async def get_headers(
    common_headers: CommonHeaders = Depends(get_common_headers)
):
    return {
        "User-Agent": common_headers.user_agent,
        "Accept-Language": common_headers.accept_language
    }

@app.get("/info")
async def get_info(
    response: Response,
    common_headers: CommonHeaders = Depends(get_common_headers)
):
    current_time = datetime.now()

    response.headers["X-Server-Time"] = current_time.isoformat()

    return {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": {
            "User-Agent": common_headers.user_agent,
            "Accept-Language": common_headers.accept_language
        },
        "server_time": current_time.isoformat()
    }

@app.get("/headers-direct")
async def get_headers_direct(
    headers: CommonHeaders = Depends() 
):
    return {
        "User-Agent": headers.user_agent,
        "Accept-Language": headers.accept_language
    }

@app.get("/")
async def root():
    return {
            "GET /headers": "Возвращает заголовки User-Agent и Accept-Language",
            "GET /info": "Возвращает заголовки + сообщение + X-Server-Time",
            "GET /headers-direct": "Альтернативная версия с прямым внедрением"
    }