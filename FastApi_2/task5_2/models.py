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

class ProfileResponse(BaseModel):
    username: str
    name: str
    email: str
    user_id: str
    message: str