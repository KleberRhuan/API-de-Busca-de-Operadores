import asyncio
from functools import lru_cache
from typing import FrozenSet, Any, Coroutine
from aiocache import cached
from sqlalchemy import Date, String
from src.domain.model.operator import Operator
from src.domain.repository.operator_repository import OperatorRepository
from src.infra.database.cache_key_manager import operator_key_builder
from src.presentation.model.operator_request_params import \
    OperatorRequestParams
from src.presentation.model.pageable_response import PageableResponse


def get_allowed_order_columns(model) -> frozenset[str]:
    return frozenset(
        col.key
        for col in model.__table__.columns
        if isinstance(col.type, (String, Date))
    )


class OperatorService:
    _ALLOWED_ORDER_COLUMNS: FrozenSet[str] = get_allowed_order_columns(Operator)

    def __init__(self, session):
        self.repository = OperatorRepository(session)

    @classmethod
    @lru_cache(maxsize=32)
    def get_allowed_columns(cls) -> frozenset[str]:
        return cls._ALLOWED_ORDER_COLUMNS

    def find_all(self, criteria: OperatorRequestParams) -> "PageableResponse":
        operators, last_page = self.repository.search_operators(criteria)
        operators_dict = [operator.model_dump(by_alias=True) for operator in operators]
        response = PageableResponse.create(operators_dict, criteria, last_page)
        return response

    """
    * @Info: Método para recuperar operadoras com cache.
    *        Tempo de TTL mais longo devido ao fato de os dados não se alterarem recorrentemente.
    """

    @cached(ttl=3600, key_builder=operator_key_builder)
    async def find_all_cached(self, criteria: OperatorRequestParams) -> PageableResponse | Any:
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, self.find_all, criteria)

        # Converter para dicionário antes de armazenar no cache
        if isinstance(response, PageableResponse):
            return response.model_dump()

        return response
