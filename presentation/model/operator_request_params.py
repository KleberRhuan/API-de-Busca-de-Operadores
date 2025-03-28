from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator
from application.exception.invalid_order_parameter_exception import InvalidOrderParameterException

class OperatorRequestParams(BaseModel):
    query: Optional[str] = Field(
        default="",
        max_length=100,
        description="Free text search across operator fields"
    )
    page: int = Field(
        default=1,
        gt=0,
        description="Page number for pagination (must be positive)"
    )
    page_size: int = Field(
        default=10,
        gt=0,
        le=100,
        description="Number of results per page (1-100)"
    )
    order_by: str = Field(
        default="razao_social",
        description="Column to order results"
    )
    order_direction: Literal["asc", "desc"] = Field(
        default="asc",
        description="Sorting direction"
    )

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