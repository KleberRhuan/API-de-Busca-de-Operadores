from pydantic import BaseModel

class OperatorModel(BaseModel):
    operator_registry: str
    tax_identifier: str
    corporate_name: str
    trade_name: str
    modality: str
    street: str
    number: str
    complement: str
    neighborhood: str
    city: str
    state: str
    zip: str
    area_code: str
    phone: str
    fax: str
    email_address: str
    representative: str
    representative_position: str
    sales_region: int