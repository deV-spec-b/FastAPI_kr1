from fastapi import FastAPI, Request, HTTPException, Header, status
from typing import Optional
import re
from .models import HeadersResponse

app = FastAPI()

def validate_accept_language(accept_language: str) -> bool:
    pattern = r'^[a-zA-Z\-]+(?:,[a-zA-Z\-]+;q=[0-9]\.[0-9])*$'
    if re.match(pattern, accept_language):
        return True
    return False

@app.get("/headers", response_model=HeadersResponse)
async def get_headers(
    user_agent: Optional[str] = Header(None, alias="User-Agent"),
    accept_language: Optional[str] = Header(None, alias="Accept-Language")
):
    if not user_agent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required header: User-Agent"
        )

    if not accept_language:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required header: Accept-Language"
        )

    if not validate_accept_language(accept_language):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Accept-Language format. Expected format: 'en-US,en;q=0.9,es;q=0.8'"
        )
    
    return HeadersResponse(
        User_Agent=user_agent,
        Accept_Language=accept_language
    )
