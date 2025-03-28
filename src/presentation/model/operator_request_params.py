from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator
from application.exception.invalid_order_parameter_exception import InvalidOrderParameterException
from fastapi import HTTPException, status

class OperatorRequestParams(BaseModel):
    query: Optional[str] = Field(
        default="",
        max_length=100,
        description="Texto livre para busca entre os campos da operadora. Mínimo de 3 caracteres quando fornecido."
    )
    page: int = Field(
        default=1,
        gt=0,
        description="Número da página para paginação. Deve ser maior que zero. A primeira página é 1."
    )
    page_size: int = Field(
        default=10,
        gt=0,
        le=100,
        description="Quantidade de resultados por página (entre 1 e 100). Valores recomendados: 10, 20, 50, 100."
    )
    order_by: Optional[str] = Field(
        default=None,
        description="Campo utilizado para ordenação dos resultados. Valores válidos incluem todos os campos de texto da operadora, como 'corporate_name', 'trade_name', 'cnpj', etc."
    )
    order_direction: Literal["asc", "desc"] = Field(
        default="asc",
        description="Direção da ordenação: 'asc' (ascendente, A-Z, 0-9) ou 'desc' (descendente, Z-A, 9-0)."
    )

    @field_validator('query')
    def validate_query_length(cls, value):
        if value and len(value) < 3:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parâmetro 'query' deve ter pelo menos 3 caracteres quando fornecido."
            )
        return value

    @field_validator('order_by')
    def validate_order_by(cls, value):
        from application.services.operator_service import OperatorSearchService
        allowed_columns = OperatorSearchService.get_allowed_columns()
        if value not in OperatorSearchService.get_allowed_columns():
            raise InvalidOrderParameterException(
                order_by=value,
                allowed=allowed_columns
            )
        return value
        
    class Config:
        schema_extra = {
            "example": {
                "query": "amil",
                "page": 1,
                "page_size": 10,
                "order_by": "corporate_name",
                "order_direction": "asc"
            }
        }