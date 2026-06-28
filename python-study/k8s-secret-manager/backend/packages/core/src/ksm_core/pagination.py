import math
from typing import TypeVar
from tortoise.models import Model
from tortoise.queryset import QuerySet

T = TypeVar("T", bound=Model)


class Paginator:
    def __init__(self, queryset: QuerySet[T], page: int = 1, size: int = 20):
        self.queryset = queryset
        self.page = max(page, 1)
        self.size = min(max(size, 1), 100)

    async def execute(self) -> dict:
        total = await self.queryset.count()
        offset = (self.page - 1) * self.size
        items = await self.queryset.offset(offset).limit(self.size)
        return {
            "items": items,
            "total": total,
            "page": self.page,
            "size": self.size,
            "pages": math.ceil(total / self.size) if total > 0 else 0,
        }
