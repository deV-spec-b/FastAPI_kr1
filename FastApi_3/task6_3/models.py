from pydantic import BaseModel, Field

class ModeInfo(BaseModel):
    mode: str = Field(..., description="DEV/PROD режим")
    docs_available: bool = Field(..., description="доступ документации")
    docs_protected: bool = Field(..., description="защищенность документации")

class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Ошибка")