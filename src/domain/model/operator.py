from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
from typing import Dict, Any
from sqlalchemy import Column, Integer, String, Date, SMALLINT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Operator(Base):
    __tablename__ = 'cadastro_operadoras'
    __table_args__ = {'schema': 'cadop'}

    id: int = Column(Integer, primary_key=True)
    operator_registry: str = Column(String, name='registro_operadora')
    cnpj: str = Column(String, name='cnpj')
    corporate_name: str = Column(String, name='razao_social')
    trade_name: str = Column(String, name='nome_fantasia')
    modality: str = Column(String, name='modalidade')
    street: str = Column(String, name='logradouro')
    number: str = Column(String, name='numero')
    complement: str = Column(String, name='complemento')
    neighborhood: str = Column(String, name='bairro')
    city: str = Column(String, name='cidade')
    state: str = Column(String, name='uf')
    zip: str = Column(String, name='cep')
    area_code: str = Column(String, name='ddd')
    phone: str = Column(String, name='telefone')
    fax: str = Column(String, name='fax')
    email: str = Column(String, name='endereco_eletronico')
    representative: str = Column(String, name='representante')
    representative_position: str = Column(String, name='cargo_representante')
    sales_region: SMALLINT = Column(SMALLINT, name='regiao_de_comercializacao')
    registration_date: Date = Column(Date, name='data_registro_ans')

    def to_dict(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
