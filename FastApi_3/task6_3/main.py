import os
import secrets
from typing import Optional
from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from .models import ModeInfo, ErrorResponse

MODE = os.getenv("MODE", "DEV").upper()
DOCS_USER = os.getenv("DOCS_USER", "admin")
DOCS_PASSWORD = os.getenv("DOCS_PASSWORD", "secret123")

app = FastAPI()

security = HTTPBasic(auto_error=False)


def check_docs_auth(credentials: Optional[HTTPBasicCredentials] = Depends(security)):
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    correct_username = secrets.compare_digest(credentials.username, DOCS_USER)
    correct_password = secrets.compare_digest(credentials.password, DOCS_PASSWORD)
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return True

@app.middleware("http")
async def docs_middleware(request: Request, call_next):
    path = request.url.path
    
    if path == "/redoc":
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Redoc documentation is disabled"}
        )
    
    is_docs_request = path == "/docs" or path == "/openapi.json"
    
    if not is_docs_request:
        return await call_next(request)
    
    if MODE == "PROD":
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Not Found"}
        )
    
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Basic "):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Not authenticated"},
            headers={"WWW-Authenticate": "Basic"}
        )
    
    import base64
    encoded = auth_header.replace("Basic ", "")
    decoded = base64.b64decode(encoded).decode("utf-8")
    username, password = decoded.split(":", 1)
    
    correct_username = secrets.compare_digest(username, DOCS_USER)
    correct_password = secrets.compare_digest(password, DOCS_PASSWORD)
    
    if not (correct_username and correct_password):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid credentials"},
            headers={"WWW-Authenticate": "Basic"}
        )
    
    return await call_next(request)

@app.get("/", summary="Информация о режиме работы")
async def root():
    return ModeInfo(
        mode=MODE,
        docs_available=(MODE == "DEV"),
        docs_protected=(MODE == "DEV")
    )


@app.get("/health", summary="Проверка работоспособности")
async def health():
    return {"status": "ok", "mode": MODE}


@app.get("/secret", summary="Пример защищенного эндпоинта")
async def get_secret():
    return {
        "message": "Это секретный эндпоинт",
        "note": "Документация защищена, а API пока открыто"
    }

if MODE not in ["DEV", "PROD"]:
    print(f"⚠️  Предупреждение: Неизвестный режим '{MODE}'")
    print("   Используется режим DEV")