from pydantic import BaseModel, Field
from typing import Optional
import uuid

class LoginData(BaseModel):
    username: str
    password: str

class User(BaseModel):
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    password: str
    name: str
    email: str
    created_at: float = Field(default_factory=lambda: __import__('time').time())

class ProfileResponse(BaseModel):
    username: str
    name: str
    email: str
    user_id: str
    time_elapsed: Optional[float] = None
    session_extended: Optional[bool] = None
    message: str