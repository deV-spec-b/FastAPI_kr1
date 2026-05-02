from pydantic import BaseModel
from typing import Any, Dict


class ErrorResponse(BaseModel):
    detail: str
    error_type: str
    status_code: int
    path: str