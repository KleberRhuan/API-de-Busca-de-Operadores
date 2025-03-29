from datetime import date
from pydantic import BaseModel, Field, field_serializer
from pydantic.alias_generators import to_camel


class OperatorModel(BaseModel):
    operator_registry: str
    cnpj: str = Field(..., description="Número do CNPJ da operadora")
    corporate_name: str
    trade_name: str | None = None
    modality: str
    street: str
    number: str
    complement: str | None = None
    neighborhood: str
    city: str
    state: str
    zip: str
    area_code: str | None = None
    phone: str | None = None
    fax: str | None = None
    email: str
    representative: str
    representative_position: str
    sales_region: int | None = None
    registration_date: date

    @field_serializer('registration_date')
    def serialize_date(self, dt: date) -> str:
        return dt.isoformat() if dt else None

    model_config = {
        "from_attributes": True,
        "alias_generator": to_camel,
        "populate_by_name": True
    }
