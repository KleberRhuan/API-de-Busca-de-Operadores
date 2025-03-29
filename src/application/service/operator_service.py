from typing import FrozenSet
from functools import lru_cache
import asyncio
from aiocache import cached, Cache
from sqlalchemy import String, Date
from src.domain.model.operator import Operator
from src.domain.repository.operator_repository import OperatorRepository
from src.infra.database.cache_key_manager import operator_key_builder
from src.presentation.model.operator_request_params import OperatorRequestParams
from src.presentation.model.pageable_response import PageableResponse

def get_allowed_order_columns(model) -> frozenset[str]:
    """
    Retorna os nomes das propriedades do modelo (em inglês) para colunas do tipo String ou Date.
    Ao invés de usar col.name (que retorna o nome da coluna no banco), usa o mapeamento
    entre propriedades Python e colunas do banco.
    """
    column_mappings = {}
    for attr_name, attr_value in model.__dict__.items():
        if hasattr(attr_value, 'property') and hasattr(attr_value.property, 'columns'):
            column = attr_value.property.columns[0]
            if isinstance(column.type, (String, Date)):
                column_mappings[attr_name] = column
    
    return frozenset(column_mappings.keys())

class OperatorService:
    _ALLOWED_ORDER_COLUMNS: FrozenSet[str] = get_allowed_order_columns(Operator)
    print(f"Allowed order columns: {_ALLOWED_ORDER_COLUMNS}")

    def __init__(self, session):
        self.repository = OperatorRepository(session)

    @classmethod
    @lru_cache(maxsize=32)  
    def get_allowed_columns(cls) -> frozenset[str]:
        return cls._ALLOWED_ORDER_COLUMNS

    def find_all(self, criteria: OperatorRequestParams) -> 'PageableResponse':
        operators, last_page = self.repository.search_operators(criteria)
        operators_dict = [operator.model_dump() for operator in operators]
        response = PageableResponse.create(operators_dict, criteria, last_page)
        return response

    """
    Tempo de TTL mais longo devido ao fato de os dados não se alterarem recorrentemente.
    """
    @cached(
        ttl=3600,
        cache=Cache.REDIS,
        key_builder=operator_key_builder
    )
    async def find_all_cached(self, criteria: OperatorRequestParams) -> dict:
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, self.find_all, criteria)
        
        # Converter para dicionário antes de armazenar no cache
        if isinstance(response, PageableResponse):
            return response.model_dump()
        
        return response
