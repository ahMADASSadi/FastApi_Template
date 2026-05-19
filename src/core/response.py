from typing import Any

from pydantic import BaseModel


class ApiResponse[T](BaseModel):
    success: bool = True
    status: int = 200
    data: T | None = None
    message: str = "success"
    error: Any | None = None
