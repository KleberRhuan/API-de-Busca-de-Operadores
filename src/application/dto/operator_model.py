from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_serializer
from pydantic.alias_generators import to_camel


class OperatorModel(BaseModel):
    operator_registry: Optional[str]
    cnpj: Optional[str] = Field(..., description="Número do CNPJ da operadora")
    corporate_name: Optional[str]
    trade_name: Optional[str]
    modality: Optional[str]
    street: Optional[str]
    number: Optional[str]
    complement: Optional[str]
    neighborhood: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip: Optional[str]
    area_code: Optional[str]
    phone: Optional[str]
    fax: Optional[str]
    email: Optional[str]
    representative: Optional[str]
    representative_position: Optional[str]
    sales_region: Optional[int]
    registration_date: date = Field(..., alias="registrationDate")

    @field_serializer("registration_date")
    def serialize_date(self, dt: date) -> str:
        return dt.isoformat() if dt else None

    model_config = {
        "from_attributes": True,
        "alias_generator": to_camel,
        "populate_by_name": True,
    }
