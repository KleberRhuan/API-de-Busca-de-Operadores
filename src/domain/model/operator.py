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

    id: int = Column('id', Integer, primary_key=True)
    operator_registry: str = Column('registro_operadora', String, key='operator_registry')
    cnpj: str = Column('cnpj', String, key='cnpj')
    corporate_name: str = Column('razao_social', String, key='corporate_name')
    trade_name: str = Column('nome_fantasia', String, key='trade_name')
    modality: str = Column('modalidade', String, key='modality')
    street: str = Column('logradouro', String, key='street')
    number: str = Column('numero', String, key='number')
    complement: str = Column('complemento', String, key='complement')
    neighborhood: str = Column('bairro', String, key='neighborhood')
    city: str = Column('cidade', String, key='city')
    state: str = Column('uf', String, key='state')
    zip: str = Column('cep', String, key='zip')
    area_code: str = Column('ddd', String, key='area_code')
    phone: str = Column('telefone', String, key='phone')
    fax: str = Column('fax', String, key='fax')
    email: str = Column('endereco_eletronico', String, key='email')
    representative: str = Column('representante', String, key='representative')
    representative_position: str = Column('cargo_representante', String, key='representative_position')
    sales_region: SMALLINT = Column('regiao_de_comercializacao', SMALLINT, key='sales_region')
    registration_date: Date = Column('data_registro_ans', Date, key='registration_date')

    def to_dict(self) -> Dict[str, Any]:
        return {c.key: getattr(self, c.key) for c in self.__table__.columns}
