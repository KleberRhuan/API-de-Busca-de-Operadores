from pydantic import BaseModel, Field

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
    area_code: str
    phone: str
    fax: str | None = None
    email: str
    representative: str
    representative_position: str
    sales_region: int
    
    class Config:
        from_attributes = True