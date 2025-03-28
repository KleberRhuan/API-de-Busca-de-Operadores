from fastapi import FastAPI
from typing import Dict, Any, List, Type
from presentation.model.pageable_response import PageableResponse
from presentation.model.operator_request_params import OperatorRequestParams
from presentation.model.pageable_meta_model import PageableMetaData, SortData
from presentation.exception.api_error import ApiError, Violation
from presentation.exception.api_error_type import ApiErrorType
from application.dto.operator_model import OperatorModel
from pydantic import create_model

def get_swagger_title() -> str:
    return "API de Busca de Operadores"

def get_rate_limit_info() -> str:
    return """
    ## Limites de Requisição
    
    Esta API utiliza limitação de taxa para garantir a disponibilidade do serviço para todos os usuários.
    
    * Endpoint `/api/v1/operators`: 10 requisições por minuto por endereço IP
    * Endpoint `/api/v1/cache-test`: 5 requisições por minuto por endereço IP
    
    Ao atingir o limite, a API retornará o código de status HTTP 429 (Too Many Requests).
    """

def get_swagger_description() -> str:
    return f"""
    API para busca de operadoras de planos de saúde registradas na ANS.
    
    ## Funcionalidades
    
    * Busca por texto livre em múltiplos campos
    * Paginação de resultados
    * Ordenação customizável
    * Cache automático para melhorar performance
    
    ## Acesso
    
    Esta API é aberta e não requer autenticação.
    
    {get_rate_limit_info()}
    
    ## Dados
    
    Os dados são extraídos diretamente das bases oficiais da ANS.
    """

def get_swagger_contact() -> Dict[str, str]:
    return {
        "name": "Kleber Rhuan",
        "url": "https://github.com/KleberRhuan",
        "email": "kleber_rhuan@hotmail.com",
    }

def get_swagger_license_info() -> Dict[str, str]:
    return {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    }

def get_swagger_tags() -> List[Dict[str, str]]:
    return [
        {
            "name": "Operadoras",
            "description": "Operações relacionadas às operadoras de planos de saúde"
        },
        {
            "name": "Desenvolvimento",
            "description": "Endpoints para suporte ao desenvolvimento e testes"
        }
    ]

def get_swagger_ui_parameters() -> Dict[str, Any]:
    return {
        "defaultModelsExpandDepth": -1,  # Esconde a seção de modelos expandida por padrão
        "persistAuthorization": False,   # Desabilita persistência de autenticação pois não é necessária
        "displayRequestDuration": True,  # Mostra duração das requisições
        "filter": True                   # Habilita filtro de busca
    }

def get_operator_model_schema() -> Dict[str, Any]:
    """
    Retorna o esquema do OperatorModel para uso nas definições do Swagger.
    Este modelo representa uma operadora de plano de saúde.
    """
    return {
        "description": "Operadora de plano de saúde",
        "type": "object",
        "properties": {
            "operator_registry": {
                "type": "string",
                "description": "Registro ANS da operadora"
            },
            "tax_identifier": {
                "type": "string",
                "description": "CNPJ da operadora"
            },
            "corporate_name": {
                "type": "string",
                "description": "Razão social da operadora"
            },
            "trade_name": {
                "type": "string",
                "description": "Nome fantasia da operadora"
            },
            "modality": {
                "type": "string",
                "description": "Modalidade da operadora (ex: Cooperativa Médica, Medicina de Grupo, etc)"
            },
            "street": {
                "type": "string",
                "description": "Nome da rua do endereço"
            },
            "number": {
                "type": "string",
                "description": "Número do endereço"
            },
            "complement": {
                "type": "string",
                "description": "Complemento do endereço"
            },
            "neighborhood": {
                "type": "string",
                "description": "Bairro do endereço"
            },
            "city": {
                "type": "string",
                "description": "Cidade do endereço"
            },
            "state": {
                "type": "string",
                "description": "Estado do endereço"
            },
            "zip": {
                "type": "string",
                "description": "CEP do endereço"
            },
            "area_code": {
                "type": "string",
                "description": "Código de área do telefone"
            },
            "phone": {
                "type": "string",
                "description": "Número de telefone"
            },
            "fax": {
                "type": "string",
                "description": "Número de fax"
            },
            "email_address": {
                "type": "string",
                "description": "Endereço de e-mail"
            },
            "representative": {
                "type": "string",
                "description": "Nome do representante legal"
            },
            "representative_position": {
                "type": "string",
                "description": "Cargo do representante legal"
            },
            "sales_region": {
                "type": "integer",
                "description": "Região de vendas"
            }
        }
    }

def get_violation_schema() -> Dict[str, Any]:
    """
    Retorna o esquema de Violation para uso nas definições de erro no Swagger.
    Este modelo representa uma violação específica em uma requisição inválida.
    """
    return {
        "description": "Violação de regra de validação",
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Nome do campo com erro"
            },
            "message": {
                "type": "string",
                "description": "Mensagem de erro descrevendo a violação"
            }
        }
    }

def get_api_error_schema() -> Dict[str, Any]:
    """
    Retorna o esquema do ApiError para uso nas definições de erro no Swagger.
    Este modelo representa um erro padronizado no formato Problem Details (RFC 7807).
    """
    return {
        "description": "Erro da API no formato Problem Details (RFC 7807)",
        "type": "object",
        "properties": {
            "status": {
                "type": "integer",
                "description": "Código HTTP do erro"
            },
            "type": {
                "type": "string",
                "description": "URI que identifica o tipo de erro"
            },
            "title": {
                "type": "string",
                "description": "Título curto e legível do erro"
            },
            "detail": {
                "type": "string",
                "description": "Explicação detalhada do erro"
            },
            "userMessage": {
                "type": "string",
                "description": "Mensagem amigável para o usuário final"
            },
            "timestamp": {
                "type": "string",
                "format": "date-time",
                "description": "Data e hora em que o erro ocorreu"
            },
            "violations": {
                "type": "array",
                "items": {
                    "$ref": "#/components/schemas/Violation"
                },
                "description": "Lista de violações específicas nos parâmetros da requisição"
            }
        }
    }

def get_operator_request_params_schema() -> Dict[str, Any]:
    """
    Retorna o esquema do OperatorRequestParams para uso nas definições de requisição no Swagger.
    Este modelo representa os parâmetros de busca para operadoras.
    """
    return {
        "description": "Parâmetros para busca de operadoras",
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Texto livre para busca entre os campos da operadora. Mínimo de 3 caracteres quando fornecido.",
                "maxLength": 100
            },
            "page": {
                "type": "integer",
                "description": "Número da página para paginação. Deve ser maior que zero. A primeira página é 1.",
                "minimum": 1,
                "default": 1
            },
            "page_size": {
                "type": "integer",
                "description": "Quantidade de resultados por página (entre 1 e 100). Valores recomendados: 10, 20, 50, 100.",
                "minimum": 1,
                "maximum": 100,
                "default": 10
            },
            "order_by": {
                "type": "string",
                "description": "Campo utilizado para ordenação dos resultados. Valores válidos incluem todos os campos de texto da operadora, como 'corporate_name', 'trade_name', 'cnpj', etc."
            },
            "order_direction": {
                "type": "string",
                "enum": ["asc", "desc"],
                "description": "Direção da ordenação: 'asc' (ascendente, A-Z, 0-9) ou 'desc' (descendente, Z-A, 9-0).",
                "default": "asc"
            }
        }
    }

def get_sort_data_schema() -> Dict[str, Any]:
    """
    Retorna o esquema do SortData para uso nas definições de paginação no Swagger.
    Este modelo representa informações de ordenação.
    """
    return {
        "description": "Informações de ordenação",
        "type": "object",
        "properties": {
            "sorted": {
                "type": "boolean",
                "description": "Indica se os resultados estão ordenados"
            },
            "property": {
                "type": "string",
                "description": "Propriedade usada para ordenação"
            },
            "dir": {
                "type": "string",
                "description": "Direção da ordenação ('asc' ou 'desc')"
            }
        }
    }

def get_pageable_meta_data_schema() -> Dict[str, Any]:
    """
    Retorna o esquema do PageableMetaData para uso nas definições de paginação no Swagger.
    Este modelo representa metadados de paginação.
    """
    return {
        "description": "Metadados de paginação",
        "type": "object",
        "properties": {
            "page": {
                "type": "integer",
                "description": "Número da página atual"
            },
            "page_size": {
                "type": "integer",
                "description": "Quantidade de itens por página"
            },
            "last_page": {
                "type": "integer",
                "description": "Número da última página disponível"
            },
            "sort": {
                "$ref": "#/components/schemas/SortData",
                "description": "Informações de ordenação"
            }
        }
    }

def get_pageable_response_schema() -> Dict[str, Any]:
    """
    Retorna o esquema do PageableResponse para uso nas definições de resposta Swagger.
    Este método padroniza o formato de resposta paginada em toda a API.
    """
    return {
        "description": "Resposta paginada",
        "content": {
            "application/json": {
                "schema": {
                    "$ref": "#/components/schemas/PageableResponse"
                },
                "example": {
                    "data": [
                        {
                            "operator_registry": "123456",
                            "tax_identifier": "12345678901234",
                            "corporate_name": "Exemplo Assistência Médica S.A.",
                            "trade_name": "Exemplo Saúde",
                            "modality": "Cooperativa Médica",
                            "street": "Avenida Brasil",
                            "number": "1000",
                            "complement": "Andar 10",
                            "neighborhood": "Centro",
                            "city": "São Paulo",
                            "state": "SP",
                            "zip": "01234567",
                            "area_code": "11",
                            "phone": "33333333",
                            "fax": "33333334",
                            "email_address": "contato@exemplo.com.br",
                            "representative": "João Silva",
                            "representative_position": "Diretor",
                            "sales_region": 1
                        }
                    ],
                    "page": 1,
                    "page_size": 10,
                    "total_pages": 1,
                    "total_items": 1,
                    "query": "exemplo",
                    "order_by": "corporate_name",
                    "order_direction": "asc"
                }
            }
        }
    }

def get_error_response_schema(status_code: int, error_type: ApiErrorType, example_detail: str = None, with_violations: bool = False) -> Dict[str, Any]:
    """
    Retorna um esquema de resposta de erro padronizado para uso nas definições de resposta Swagger.
    
    Args:
        status_code: Código HTTP do erro
        error_type: Tipo de erro da enum ApiErrorType
        example_detail: Detalhe de exemplo para o erro
        with_violations: Se deve incluir violações de exemplo
        
    Returns:
        Esquema de resposta de erro formatado
    """
    content_example = {
        "status": status_code,
        "type": f"https://api.intuitivecare.com.br{error_type.value}",
        "title": error_type.title,
        "detail": example_detail or f"Exemplo de erro do tipo {error_type.title}",
        "timestamp": "2023-03-27T14:30:00Z"
    }
    
    if error_type == ApiErrorType.SYSTEM_ERROR:
        content_example["userMessage"] = "Ocorreu um erro interno no servidor, tente novamente e se o problema persistir, entre em contato com o administrador."
    
    if with_violations:
        content_example["violations"] = [
            {"name": "campo1", "message": "deve ser preenchido"},
            {"name": "campo2", "message": "deve ser um número válido"}
        ]
    
    return {
        "description": error_type.title,
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/ApiError"},
                "example": content_example
            }
        }
    }

def get_error_response_schema_for_rate_limit() -> Dict[str, Any]:
    """
    Retorna o esquema da resposta para o erro de rate limit
    """
    return {
        "description": "Muitas requisições (rate limit excedido)",
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/ApiError"},
                "example": {
                    "status": 429,
                    "type": "https://api.intuitivecare.com.br/rate-limit-excedido",
                    "title": "Limite de Requisições Excedido",
                    "detail": "Você excedeu o limite de 10 requisições por minuto. Tente novamente em 45 segundos.",
                    "userMessage": "Limite de requisições excedido. Aguarde um momento antes de tentar novamente.",
                    "timestamp": "2023-03-27T14:30:00Z"
                }
            }
        },
        "headers": {
            "X-RateLimit-Limit": {
                "description": "Número máximo de requisições permitidas no período",
                "schema": {"type": "integer"}
            },
            "X-RateLimit-Remaining": {
                "description": "Número de requisições restantes no período atual",
                "schema": {"type": "integer"}
            },
            "X-RateLimit-Reset": {
                "description": "Tempo (em segundos) até o reset do limite",
                "schema": {"type": "integer"}
            },
            "Retry-After": {
                "description": "Tempo recomendado (em segundos) para aguardar antes de tentar novamente",
                "schema": {"type": "integer"}
            }
        }
    }

def get_common_error_responses() -> Dict[int, Dict[str, Any]]:
    """
    Retorna um conjunto de respostas de erro comuns para uso em todos os endpoints.
    """
    responses = {
        400: get_error_response_schema(
            400, 
            ApiErrorType.INVALID_PARAMETER, 
            "Parâmetro de ordenação inválido. Valores permitidos: corporate_name, trade_name, cnpj"
        ),
        404: get_error_response_schema(
            404, 
            ApiErrorType.RESOURCE_NOT_FOUND, 
            "O recurso solicitado não foi encontrado"
        ),
        422: get_error_response_schema(
            422, 
            ApiErrorType.MESSAGE_NOT_READABLE, 
            "Erro de validação nos parâmetros da requisição",
            True
        ),
        429: get_error_response_schema_for_rate_limit(),
        500: get_error_response_schema(
            500, 
            ApiErrorType.SYSTEM_ERROR, 
            "Erro interno do servidor"
        )
    }
    return responses

def get_swagger_responses_for_operators() -> Dict[int, Dict[str, Any]]:
    responses = get_common_error_responses()
    
    # Utiliza o esquema padronizado para respostas paginadas
    responses[200] = get_pageable_response_schema()
    
    return responses

def get_swagger_responses_for_cache_test() -> Dict[int, Dict[str, Any]]:
    responses = {
        500: get_error_response_schema(
            500, 
            ApiErrorType.SYSTEM_ERROR, 
            "Erro ao acessar o cache"
        ),
        200: {
            "description": "Teste de cache bem-sucedido",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "cached_value": {
                            "message": "Cache is working!"
                        }
                    }
                }
            }
        }
    }
    
    return responses

def get_operators_endpoint_description() -> str:
    return """
    Retorna uma lista paginada de operadoras de planos de saúde com base nos parâmetros fornecidos.
    
    A busca pode ser realizada por texto livre que será pesquisado em diversos campos como razão social, 
    nome fantasia, CNPJ, etc. Os resultados são retornados em formato paginado.
    """

def get_cache_test_endpoint_description() -> str:
    return "Endpoint para teste do sistema de cache Redis"

def get_operators_endpoint_docstring() -> str:
    return """
    Busca operadoras de planos de saúde.
    
    - **query**: Texto para busca em diversos campos (razão social, nome fantasia, etc)
    - **page**: Número da página (começando em 1)
    - **page_size**: Quantidade de itens por página (entre 1 e 100)
    - **order_by**: Campo para ordenação dos resultados
    - **order_direction**: Direção da ordenação ("asc" ou "desc")
    """

def get_cache_test_endpoint_docstring() -> str:
    return """
    Testa a funcionalidade de cache da aplicação.
    
    Este endpoint adiciona um valor ao cache, recupera-o e retorna o valor recuperado.
    Útil para diagnóstico do sistema de cache.
    """

# Dicionário com todas as configurações de endpoints para facilitar o acesso
ENDPOINT_CONFIG = {
    "operators": {
        "tag": "Operadoras",
        "summary": "Buscar operadoras",
        "description": get_operators_endpoint_description(),
        "response_description": "Lista paginada de operadoras",
        "responses": get_swagger_responses_for_operators(),
        "docstring": get_operators_endpoint_docstring(),
        "response_model": PageableResponse,
        "request_params_model": OperatorRequestParams
    },
    "cache_test": {
        "tag": "Desenvolvimento",
        "summary": "Testar cache",
        "description": get_cache_test_endpoint_description(),
        "response_description": "Resultado do teste de cache",
        "responses": get_swagger_responses_for_cache_test(),
        "docstring": get_cache_test_endpoint_docstring()
    }
}

def configure_swagger(app: FastAPI) -> None:
    """
    Configura os parâmetros do Swagger para o aplicativo FastAPI.
    
    Args:
        app: Instância do FastAPI para configurar
    """
    app.title = get_swagger_title()
    app.description = get_swagger_description()
    app.version = "1.0.0"
    app.contact = get_swagger_contact()
    app.license_info = get_swagger_license_info()
    app.openapi_tags = get_swagger_tags()
    
    # Configurações adicionais da UI do Swagger
    app.swagger_ui_parameters = get_swagger_ui_parameters()
    
    # Registro explícito dos modelos nos componentes do schema
    app.components = {
        "schemas": {
            # Modelos de domínio
            "OperatorModel": OperatorModel.model_json_schema(),
            
            # Modelos de apresentação
            "PageableResponse": PageableResponse.model_json_schema(),
            "PageableMetaData": PageableMetaData.model_json_schema(),
            "SortData": SortData.model_json_schema(),
            "OperatorRequestParams": OperatorRequestParams.model_json_schema(),
            
            # Modelos de erro
            "ApiError": ApiError.model_json_schema(),
            "Violation": Violation.model_json_schema(),
        }
    } 