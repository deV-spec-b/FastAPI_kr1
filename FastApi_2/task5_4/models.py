from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re

class HeadersResponse(BaseModel):
    User_Agent: str = Field(..., alias="User-Agent")
    Accept_Language: str = Field(..., alias="Accept-Language")
    
    class Config:
        populate_by_name = True