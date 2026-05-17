from typing import Any

from fastapi.exceptions import HTTPException


class BaseException(HTTPException):
    def __init__(self, status_code: int, detail: Any, headers: dict[str, str] | None) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)
