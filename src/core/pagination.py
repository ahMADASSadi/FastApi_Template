from fastapi import Query
from fastapi_pagination import Params


class PaginationParams(Params):
    page: int = Query(1, ge=1)
    size: int = Query(10, ge=1, le=100)
