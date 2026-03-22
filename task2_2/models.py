from pydantic import BaseModel, Field, field_validator

class Feedback(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    message: str = Field(..., min_length=10, max_length=500)
    
    @field_validator('message')
    @classmethod
    def check_bad_words(cls, v: str) -> str:
        bad_words = ['кринж', 'рофл', 'вайб']
        if any(word in v.lower() for word in bad_words):
            raise ValueError('Использование недопустимых слов')
        return v