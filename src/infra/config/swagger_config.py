import os
from typing import Any, Dict, List

from fastapi import FastAPI

from src.application.dto.operator_model import OperatorModel
from src.presentation.exception.api_error import ApiError, Violation
from src.presentation.exception.api_error_type import ApiErrorType
from src.presentation.model.operator_request_params import \
    OperatorRequestParams
from src.presentation.model.pageable_response import PageableResponse


def get_swagger_title() -> str:
    return "API de Busca de Operadores"


def get_rate_limit_info() -> str:
    rate_limit = int(os.getenv("RATE_LIMIT", "100"))
    rate_window = int(os.getenv("RATE_WINDOW", "60"))

    return f"""
    ## Limites de Requisição
    
    Esta API utiliza limitação de taxa para garantir a disponibilidade do serviço para todos os usuários.
    
    * Endpoint `/api/v1/operators`: {rate_limit} requisições por {rate_window} segundos por endereço IP
    * Endpoint `/api/v1/cache-test`: {rate_limit} requisições por {rate_window} segundos por endereço IP
    
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
    * Rate limiting com headers compatíveis com RFC 6585
    * Respostas em formato JSON com convenção camelCase
    
    ## CORS e Requisições OPTIONS
    
    Esta API implementa CORS (Cross-Origin Resource Sharing) para permitir acesso de origens diferentes.
    O FastAPI e Starlette implementam suporte a requisições OPTIONS, mas para que funcionem corretamente:
    
    * As requisições devem incluir os cabeçalhos `Origin` e `Access-Control-Request-Method`
    * Apenas os métodos GET e OPTIONS são permitidos
    * Para mais detalhes, consulte a documentação em `/docs/cors-configuration.md`
    
    ## Convenção camelCase
    
    Todas as respostas JSON desta API utilizam a convenção camelCase para nomes de propriedades.
    Para mais detalhes, consulte a documentação em `/docs/camelCase-convention.md`.
    
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
            "description": "Operações relacionadas às operadoras de planos de saúde",
        },
        {
            "name": "Desenvolvimento",
            "description": "Endpoints para suporte ao desenvolvimento e testes",
        },
    ]


def get_swagger_ui_parameters() -> Dict[str, Any]:
    return {
        "defaultModelsExpandDepth": -1,
        "persistAuthorization": False,  # Desabilita persistência de autenticação pois não é necessária
        "displayRequestDuration": True,
        "filter": True,
        "syntaxHighlight": {"activate": True, "theme": "monokai"},
        "docExpansion": "list",
        "deepLinking": True,
        "showExtensions": True,
        "showCommonExtensions": True,
        "tryItOutEnabled": True,
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
            "operatorRegistry": {
                "type": "string",
                "description": "Registro ANS da operadora",
            },
            "cnpj": {"type": "string", "description": "CNPJ da operadora"},
            "corporateName": {
                "type": "string",
                "description": "Razão social da operadora",
            },
            "tradeName": {
                "type": "string",
                "description": "Nome fantasia da operadora",
            },
            "modality": {
                "type": "string",
                "description": "Modalidade da operadora (ex: Cooperativa Médica, Medicina de Grupo, etc)",
            },
            "street": {"type": "string", "description": "Nome da rua do endereço"},
            "number": {"type": "string", "description": "Número do endereço"},
            "complement": {"type": "string", "description": "Complemento do endereço"},
            "neighborhood": {"type": "string", "description": "Bairro do endereço"},
            "city": {"type": "string", "description": "Cidade do endereço"},
            "state": {"type": "string", "description": "Estado do endereço"},
            "zip": {"type": "string", "description": "CEP do endereço"},
            "areaCode": {"type": "string", "description": "Código de área do telefone"},
            "phone": {"type": "string", "description": "Número de telefone"},
            "fax": {"type": "string", "description": "Número de fax"},
            "email": {"type": "string", "description": "Endereço de e-mail"},
            "representative": {
                "type": "string",
                "description": "Nome do representante legal",
            },
            "representativePosition": {
                "type": "string",
                "description": "Cargo do representante legal",
            },
            "salesRegion": {"type": "integer", "description": "Região de vendas"},
            "registrationDate": {
                "type": "string",
                "format": "date",
                "description": "Data de registro na ANS",
            },
        },
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
            "name": {"type": "string", "description": "Nome do campo com erro"},
            "message": {
                "type": "string",
                "description": "Mensagem de erro descrevendo a violação",
            },
        },
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
            "status": {"type": "integer", "description": "Código HTTP do erro"},
            "type": {
                "type": "string",
                "description": "URI que identifica o tipo de erro",
            },
            "title": {
                "type": "string",
                "description": "Título curto e legível do erro",
            },
            "detail": {"type": "string", "description": "Explicação detalhada do erro"},
            "userMessage": {
                "type": "string",
                "description": "Mensagem amigável para o usuário final",
            },
            "timestamp": {
                "type": "string",
                "format": "date-time",
                "description": "Data e hora em que o erro ocorreu",
            },
            "violations": {
                "type": "array",
                "items": {"$ref": "#/components/schemas/Violation"},
                "description": "Lista de violações específicas nos parâmetros da requisição",
            },
        },
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
            "search": {
                "type": "string",
                "description": "Texto livre para busca entre os campos da operadora. Mínimo de 2 caracteres quando fornecido, permitindo busca por siglas de estados (UF).",
                "maxLength": 100,
            },
            "page": {
                "type": "integer",
                "description": "Número da página para paginação. Deve ser maior que zero. A primeira página é 1.",
                "minimum": 1,
                "default": 1,
            },
            "pageSize": {
                "type": "integer",
                "description": "Quantidade de resultados por página (entre 1 e 100). Valores recomendados: 10, 20, 50, 100.",
                "minimum": 1,
                "maximum": 100,
                "default": 10,
            },
            "sortField": {
                "type": "string",
                "description": "Campo utilizado para ordenação dos resultados. Valores válidos incluem: corporateName, tradeName, cnpj, operatorRegistry, city, state, registrationDate.",
                "enum": [
                    "corporateName",
                    "tradeName",
                    "cnpj",
                    "operatorRegistry",
                    "city",
                    "state",
                    "registrationDate",
                ],
            },
            "sortDirection": {
                "type": "string",
                "enum": ["asc", "desc"],
                "description": "Direção da ordenação: 'asc' (ascendente, A-Z, 0-9) ou 'desc' (descendente, Z-A, 9-0).",
                "default": "asc",
            },
        },
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
                "schema": {"$ref": "#/components/schemas/PageableResponse"},
                "example": {
                    "data": [
                        {
                            "operatorRegistry": "123456",
                            "cnpj": "12345678901234",
                            "corporateName": "Exemplo Assistência Médica S.A.",
                            "tradeName": "Exemplo Saúde",
                            "modality": "Cooperativa Médica",
                            "street": "Avenida Brasil",
                            "number": "1000",
                            "complement": "Andar 10",
                            "neighborhood": "Centro",
                            "city": "São Paulo",
                            "state": "SP",
                            "zip": "01234567",
                            "areaCode": "11",
                            "phone": "33333333",
                            "fax": "33333334",
                            "email": "contato@exemplo.com.br",
                            "representative": "João Silva",
                            "representativePosition": "Diretor",
                            "salesRegion": 1,
                            "registrationDate": "2020-01-01",
                        }
                    ],
                    "page": 1,
                    "pageSize": 10,
                    "totalPages": 1,
                    "totalItems": 1,
                    "search": "exemplo",
                    "sortField": "corporateName",
                    "sortDirection": "asc",
                },
            }
        },
    }


def get_error_response_schema(
    status_code: int,
    error_type: ApiErrorType,
    example_detail: str = None,
    with_violations: bool = False,
) -> Dict[str, Any]:
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

    api_error_schema = {
        "type": "object",
        "properties": {
            "status": {
                "type": "integer",
                "description": "Código HTTP do erro",
                "example": status_code,
            },
            "type": {
                "type": "string",
                "description": "URI que identifica o tipo de erro",
                "example": f"https://localhost:8080{error_type.value}",
            },
            "title": {
                "type": "string",
                "description": "Título curto e legível do erro",
                "example": error_type.title,
            },
            "detail": {
                "type": "string",
                "description": "Explicação detalhada do erro",
                "example": example_detail
                or f"Exemplo de erro do tipo {error_type.title}",
            },
            "timestamp": {
                "type": "string",
                "format": "date-time",
                "description": "Data e hora em que o erro ocorreu",
                "example": "2025-03-27T14:30:00Z",
            },
        },
        "required": ["status", "type", "title", "detail", "timestamp"],
    }

    if error_type == ApiErrorType.SYSTEM_ERROR:
        api_error_schema["properties"]["userMessage"] = {
            "type": "string",
            "description": "Mensagem amigável para o usuário final",
            "example": "Ocorreu um erro interno no servidor, tente novamente e se o problema persistir, entre em contato com o administrador.",
        }

    if with_violations:
        api_error_schema["properties"]["violations"] = {
            "type": "array",
            "description": "Lista de violações específicas nos parâmetros da requisição",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Nome do campo com erro",
                        "example": "search",
                    },
                    "message": {
                        "type": "string",
                        "description": "Mensagem de erro descrevendo a violação",
                        "example": "O parâmetro 'search' deve ter pelo menos 2 caracteres.",
                    },
                },
            },
            "example": [
                {
                    "name": "search",
                    "message": "O parâmetro 'search' deve ter pelo menos 2 caracteres.",
                },
                {"name": "page", "message": "deve ser um número maior que zero"},
            ],
        }

    return {
        "description": error_type.title,
        "content": {"application/json": {"schema": api_error_schema}},
    }


def get_error_response_schema_for_rate_limit() -> Dict[str, Any]:
    """
    Retorna o esquema de resposta de erro específico para limite de taxa excedido (429 Too Many Requests)
    """
    rate_limit = int(os.getenv("RATE_LIMIT", "100"))
    rate_window = int(os.getenv("RATE_WINDOW", "60"))

    example_detail = f"Taxa de requisições excedida. Limite de {rate_limit} requisições por {rate_window} segundos."

    schema = get_error_response_schema(
        429, ApiErrorType.RATE_LIMIT_EXCEEDED, example_detail
    )

    # Adicionar informações sobre os cabeçalhos de rate limit
    schema["headers"] = {
        "Retry-After": {
            "description": "Tempo em segundos até que o limite seja resetado",
            "schema": {"type": "integer"},
        },
        "X-RateLimit-Limit": {
            "description": "Número máximo de requisições permitidas por período",
            "schema": {"type": "integer"},
        },
        "X-RateLimit-Remaining": {
            "description": "Número de requisições restantes no período atual",
            "schema": {"type": "integer"},
        },
        "X-RateLimit-Reset": {
            "description": "Tempo em segundos até o reset do limite",
            "schema": {"type": "integer"},
        },
    }

    return schema


def get_common_error_responses() -> Dict[int, Dict[str, Any]]:
    """
    Retorna um conjunto de respostas de erro comuns para uso em todos os endpoints.
    """
    responses = {
        400: get_error_response_schema(
            400,
            ApiErrorType.INVALID_PARAMETER,
            "Parâmetro de ordenação inválido. Valores permitidos: corporateName, tradeName, cnpj",
        ),
        404: get_error_response_schema(
            404,
            ApiErrorType.RESOURCE_NOT_FOUND,
            "O recurso solicitado não foi encontrado",
        ),
        422: get_error_response_schema(
            422,
            ApiErrorType.MESSAGE_NOT_READABLE,
            "Erro de validação nos parâmetros da requisição",
            True,
        ),
        429: get_error_response_schema_for_rate_limit(),
        500: get_error_response_schema(
            500, ApiErrorType.SYSTEM_ERROR, "Erro interno do servidor"
        ),
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
            500, ApiErrorType.SYSTEM_ERROR, "Erro ao acessar o cache"
        ),
        200: {
            "description": "Teste de cache bem-sucedido",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "cached_value": {"message": "Cache is working!"},
                    }
                }
            },
        },
    }

    return responses


def get_operators_endpoint_description() -> str:
    rate_limit = int(os.getenv("RATE_LIMIT", "100"))
    rate_window = int(os.getenv("RATE_WINDOW", "60"))

    return f"""
    Retorna uma lista paginada de operadoras de planos de saúde com base nos parâmetros fornecidos.
    
    A busca pode ser realizada por texto livre que será pesquisado em diversos campos como:
    - Razão social (corporateName)
    - Nome fantasia (tradeName)
    - CNPJ (cnpj)
    - Registro ANS (operatorRegistry)
    - Cidade (city)
    - Estado (state) - É possível buscar por siglas de estados brasileiros com 2 caracteres, como "SP", "RJ", "MG", etc.
    
    Os resultados podem ser ordenados pelos campos acima e também por:
    - Data de registro (registrationDate)
    
    Os resultados são retornados em formato paginado.
    
    **Observação**: Este endpoint está sujeito a limite de taxa de {rate_limit} requisições por {rate_window} segundos por endereço IP.
    """


def get_cache_test_endpoint_description() -> str:
    return "Endpoint para teste do sistema de cache Redis"


def get_operators_endpoint_docstring() -> str:
    return """
    Busca operadoras de planos de saúde.
    
    - **search**: Texto para busca em diversos campos (mínimo 2 caracteres)
    - **page**: Número da página (começando em 1)
    - **pageSize**: Quantidade de itens por página (entre 1 e 100)
    - **sortField**: Campo para ordenação dos resultados
    - **sortDirection**: Direção da ordenação ("asc" ou "desc")
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
        "request_params_model": OperatorRequestParams,
    },
    "cache_test": {
        "tag": "Desenvolvimento",
        "summary": "Testar cache",
        "description": get_cache_test_endpoint_description(),
        "response_description": "Resultado do teste de cache",
        "responses": get_swagger_responses_for_cache_test(),
        "docstring": get_cache_test_endpoint_docstring(),
    },
    "health": {
        "tag": "Health",
        "summary": "Health Check",
        "description": "Endpoint that returns the health status of the API.",
        "response_description": "Health status response",
        "responses": {
            200: {
                "description": "API is healthy",
                "content": {
                    "application/json": {
                        "example": {"status": "ok"}
                    }
                }
            }
        },
        "docstring": "Health check endpoint"
    },
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

    # Aplicar um tema personalizado
    app.swagger_ui_oauth2_redirect_url = "/docs/oauth2-redirect"
    app.swagger_ui_init_oauth = {"usePkceWithAuthorizationCodeGrant": True}

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = app.__class__.openapi(app)

        if "components" not in openapi_schema:
            openapi_schema["components"] = {}

        if "schemas" not in openapi_schema["components"]:
            openapi_schema["components"]["schemas"] = {}

        openapi_schema["components"]["schemas"][
            "OperatorModel"
        ] = OperatorModel.model_json_schema()
        openapi_schema["components"]["schemas"][
            "PageableResponse"
        ] = PageableResponse.model_json_schema()
        openapi_schema["components"]["schemas"][
            "OperatorRequestParams"
        ] = OperatorRequestParams.model_json_schema()
        openapi_schema["components"]["schemas"][
            "ApiError"
        ] = ApiError.model_json_schema()
        openapi_schema["components"]["schemas"][
            "Violation"
        ] = Violation.model_json_schema()

        openapi_schema["info"]["x-theme"] = {
            "colors": {
                "primary": "#c1c1c1",  # Cor primária (botões, links)
                "secondary": "#0077cc",  # Cor secundária
                "success": "#32a852",  # Cor de sucesso
                "warning": "#f0ad4e",  # Cor de aviso
                "error": "#d9534f",  # Cor de erro
                "background": "#ffffff",  # Cor de fundo
            },
            "typography": {
                "fontSize": "14px",
                "fontFamily": "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
            },
        }

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

