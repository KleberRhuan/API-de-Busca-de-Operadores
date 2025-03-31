from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator
from pydantic.alias_generators import to_camel

from src.application.exception.invalid_sort_parameter_exception import \
    InvalidSortParameterException
from src.application.exception.violation_exception import ViolationException


class OperatorRequestParams(BaseModel):
    search: Optional[str] = Field(
        default="",
        max_length=100,
        description="Texto livre para busca entre os campos da operadora. Mínimo de 2 caracteres quando fornecido, permitindo busca por siglas de estados (UF).",
    )
    page: int = Field(
        default=1,
        gt=0,
        description="Número da página para paginação. Deve ser maior que zero. A primeira página é 1.",
    )
    page_size: int = Field(
        default=10,
        gt=0,
        le=100,
        description="Quantidade de resultados por página (entre 1 e 100). Valores recomendados: 10, 20, 50, 100.",
    )
    sort_field: Optional[str] = Field(
        default=None,
        description="Campo utilizado para ordenação dos resultados. Valores válidos incluem todos os campos de texto da operadora, como 'corporate_name', 'trade_name', 'cnpj', etc.",
    )
    sort_direction: Literal["asc", "desc"] = Field(
        default="asc",
        description="Direção da ordenação: 'asc' (ascendente, A-Z, 0-9) ou 'desc' (descendente, Z-A, 9-0).",
    )

    @field_validator("search")
    def validate_search_length(cls, value):
        if value and len(value) < 2:
            raise ViolationException(
                field="search",
                message="O parâmetro 'search' deve ter pelo menos 2 caracteres.",
            )
        return value

    @field_validator("sort_field")
    def validate_sort_field(cls, value):
        if value is None:
            return value

        from src.application.service.operator_service import OperatorService

        allowed_columns = OperatorService.get_allowed_columns()
        if value not in allowed_columns:
            raise InvalidSortParameterException(
                field="sort_field",
                message=f"O parâmetro 'sort_field' deve ser um dos seguintes: {', '.join(allowed_columns)}",
            )
        return value

    model_config = {
        "from_attributes": True,
        "alias_generator": to_camel,
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "search": "SP",
                "page": 1,
                "pageSize": 10,
                "sortField": "state",
                "sortDirection": "asc",
            }
        },
    }
