from typing import FrozenSet
from functools import lru_cache
import asyncio
from aiocache import cached, Cache
from sqlalchemy import String
from domain.model.operator import Operator
from domain.repository.operator_repository import OperatorRepository
from presentation.model.operator_request_params import OperatorRequestParams
from presentation.model.pageable_response import PageableResponse

def get_allowed_order_columns(model) -> frozenset[str]:
    return frozenset(
        col.name for col in model.__table__.columns if isinstance(col.type, String)
    )

class OperatorSearchService:
    _ALLOWED_ORDER_COLUMNS: FrozenSet[str] = get_allowed_order_columns(Operator)

    def __init__(self, repository: OperatorRepository):
        self.repository = repository

    @classmethod
    @lru_cache(maxsize=1)
    def get_allowed_columns(cls) -> frozenset[str]:
        return cls._ALLOWED_ORDER_COLUMNS

    def find_all(self, criteria: OperatorRequestParams) -> 'PageableResponse':
        operators, last_page = self.repository.search_operators(criteria)
        response = PageableResponse.create(operators, criteria, last_page)
        return response

    """
    Tempo de TTL mais longo devido ao fato de os dados não se alterarem recorrentemente.
    """
    @cached(
        ttl=3600,
        cache=Cache.REDIS,
        key_builder=lambda f, *args, **kwargs: f"operator_search:{kwargs['criteria'].json()}"
    )
    async def find_all_cached(self, criteria: OperatorRequestParams) -> 'PageableResponse':
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, self.find_all, criteria)
        return response
