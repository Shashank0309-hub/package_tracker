from typing import Any, Optional

from pydantic import BaseModel
from starlette.status import HTTP_200_OK


class GlobalResponse(BaseModel):
    data: Any
    status: int = HTTP_200_OK
    message: Optional[str]


class Pagination(BaseModel):
    page: Optional[int] = 0
    limit: Optional[int] = 25
    total: Optional[int]


class PaginatedResponse(GlobalResponse):
    meta: Pagination
