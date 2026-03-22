from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re

class CommonHeaders(BaseModel):
    user_agent: str = Field(..., alias="User-Agent", description="User-Agent заголовок")
    accept_language: str = Field(..., alias="Accept-Language", description="Accept-Language заголовок")
    
    @field_validator('accept_language')
    @classmethod
    def validate_accept_language(cls, v: str) -> str:
        if not v:
            raise ValueError('Accept-Language заголовок обязателен')

        pattern = r'^[a-zA-Z\-]+(?:,[a-zA-Z\-]+;q=[0-9]\.[0-9])*$'
        
        if not re.match(pattern, v):
            raise ValueError(
                f'Неверный формат Accept-Language: "{v}". '
                f'Ожидаемый формат: "en-US,en;q=0.9,es;q=0.8"'
            )
        
        return v
    
    class Config:
        populate_by_name = True
        extra = "forbid"  