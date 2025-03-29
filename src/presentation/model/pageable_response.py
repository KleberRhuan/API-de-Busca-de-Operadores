from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel


class PageableResponse(BaseModel):
    """
    Resposta paginada da API de busca de operadoras.
    
    Este modelo representa a estrutura da resposta retornada pelo endpoint de busca,
    incluindo os dados das operadoras e informações de paginação.
    """
    
    data: List[Dict[str, Any]] = Field(
        description="Lista de operadoras encontradas. Cada operadora é representada como um objeto com seus atributos."
    )
    page: int = Field(
        description="Página atual da resposta. Começa em 1."
    )
    page_size: int = Field(
        description="Quantidade de itens por página. Valor usado na consulta."
    )
    total_pages: int = Field(
        description="Número total de páginas disponíveis para a consulta."
    )
    total_items: int = Field(
        description="Número total de operadoras encontradas para a consulta."
    )
    search: str = Field(
        description="Texto de busca utilizado na consulta. String vazia se nenhuma busca textual foi realizada."
    )
    sort_field: Optional[str] = Field(
        description="Campo utilizado para ordenação dos resultados. Null se nenhuma ordenação específica foi solicitada."
    )
    sort_direction: str = Field(
        description="Direção da ordenação ('asc' ou 'desc')."
    )

    @classmethod
    def create(cls, operators: List[Dict[str, Any]], params, last_page: int) -> 'PageableResponse':
        """
        Cria uma resposta paginada a partir dos dados dos operadores e parâmetros de consulta.
        
        Args:
            operators: Lista de dicionários contendo os dados das operadoras
            params: Parâmetros da requisição
            last_page: Número total de páginas
            
        Returns:
            Uma instância de PageableResponse configurada com os dados fornecidos
        """
        total_items = (last_page - 1) * params.page_size + len(operators) if operators else 0
        
        return cls(
            data=operators,
            page=params.page,
            page_size=params.page_size,
            total_pages=last_page,
            total_items=total_items,
            search=params.search,
            sort_field=params.sort_field,
            sort_direction=params.sort_direction
        )

    model_config = {
        "from_attributes": True,
        "alias_generator": to_camel,
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "data": [
                    {
                        "id": 1,
                        "operator_registry": "123456",
                        "cnpj": "12345678901234",
                        "corporate_name": "Amil Assistência Médica Internacional S.A.",
                        "trade_name": "Amil",
                        "modality": "Seguradora Especializada em Saúde",
                        "street": "Avenida Brasil",
                        "number": "1000",
                        "complement": "Andar 10",
                        "neighborhood": "Centro",
                        "city": "São Paulo",
                        "state": "SP",
                        "zip": "01234567",
                        "email": "contato@amil.com.br"
                    }
                ],
                "page": 1,
                "page_size": 10,
                "total_pages": 1,
                "total_items": 1,
                "search": "amil",
                "sort_field": "corporate_name",
                "sort_direction": "asc"
            }
        }
    }
