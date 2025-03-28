from datetime import datetime, UTC
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_serializer, model_validator

from infra.config import Config


class Violation(BaseModel):
    name: str
    message: str

"""
* @Author: Kleber Rhuan
* @Date: 2025-27-03
* @Description: Representa um corpo de resposta de erro padronizado, conforme o formato Problem Details definido na RFC 7807.
* Esse registro fornece informações de erro consistentes e detalhadas na resposta da API.
"""
class ApiError(BaseModel):
    status: int
    type: str
    title: str
    detail: str

    # Campos adicionais
    userMessage: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    violations: Optional[List[Violation]] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True, 
        frozen=True)

    @field_serializer('timestamp')
    def serialize_timestamp(self, timestamp: datetime, _info):
        return timestamp.isoformat()


    @model_validator(mode="before")
    def add_url_to_type(cls, values):
        base_url = Config.APP_URL
        if "type" in values and values["type"]:
            values["type"] = f"{base_url}{values['type']}"
        return values