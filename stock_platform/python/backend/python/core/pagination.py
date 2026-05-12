from dataclasses import dataclass
from fastapi import Query
from typing import Optional


@dataclass
class PaginationParams:
    page: int
    per_page: int


def pagination_params(
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(20, ge=1, le=100, description="每页数量"),
) -> PaginationParams:
    return PaginationParams(page=page, per_page=per_page)