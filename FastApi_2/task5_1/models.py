from pydantic import BaseModel
from typing import Optional

class LoginData(BaseModel):
    username: str
    password: str

class UserProfile(BaseModel):
    username: str
    name: str
    message: str