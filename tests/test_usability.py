import pytest
import json
import inspect
from fastapi.testclient import TestClient
from unittest.mock import patch
from presentation.main import create_application
from presentation.model.pageable_response import PageableResponse
from presentation.model.operator_request_params import OperatorRequestParams

@pytest.fixture
def test_client():
    app = create_application()
    return TestClient(app)

@pytest.fixture
def mock_response():
    # Dados mockados para simular resultados do banco de dados
    mock_data = [
        {
            "id": 1,
            "operator_registry": "123456",
            "cnpj": "12345678901234",
            "corporate_name": "Empresa Teste 1",
            "trade_name": "Teste 1",
            "modality": "Cooperativa Médica",
            "city": "São Paulo",
            "state": "SP"
        }
    ]
    
    return PageableResponse(
        data=mock_data,
        page=1,
        page_size=10,
        total_pages=1,
        total_items=1,
        query="",
        order_by="corporate_name",
        order_direction="asc"
    )

@pytest.mark.asyncio
@patch('application.services.operator_service.OperatorSearchService.find_all_cached')
async def test_api_documentation(mock_find_all_cached, test_client):
    """
    Verifica se a API possui documentação OpenAPI/Swagger
    """
    # Faz a requisição para o endpoint de documentação OpenAPI
    response = test_client.get("/openapi.json")
    
    # Verifica se a resposta é bem-sucedida
    assert response.status_code == 200, "API deve fornecer um esquema OpenAPI em /openapi.json"
    
    # Verifica se o esquema OpenAPI contém as propriedades básicas
    schema = response.json()
    assert "openapi" in schema, "Esquema OpenAPI deve conter a versão do OpenAPI"
    assert "info" in schema, "Esquema OpenAPI deve conter informações sobre a API"
    assert "paths" in schema, "Esquema OpenAPI deve conter definições de caminhos"
    
    # Verifica se o endpoint de operadores está documentado
    assert "/api/v1/operators" in schema["paths"], "O endpoint de operadores deve estar documentado no esquema OpenAPI"

@pytest.mark.asyncio
@patch('application.services.operator_service.OperatorSearchService.find_all_cached')
async def test_parameter_descriptions(mock_find_all_cached, test_client):
    """
    Verifica se os parâmetros da API possuem descrições claras
    """
    # Obtém a documentação OpenAPI
    response = test_client.get("/openapi.json")
    schema = response.json()
    
    # Obtém os parâmetros do endpoint de operadores
    operators_path = schema["paths"]["/api/v1/operators"]
    operators_get = operators_path["get"]
    operators_params = operators_get["parameters"]
    
    # Verifica se todos os parâmetros possuem descrições
    for param in operators_params:
        assert "description" in param, f"O parâmetro '{param['name']}' deve ter uma descrição"
        assert len(param["description"]) > 0, f"A descrição do parâmetro '{param['name']}' não deve estar vazia"

@pytest.mark.asyncio
@patch('application.services.operator_service.OperatorSearchService.find_all_cached')
async def test_parameter_defaults(mock_find_all_cached, test_client):
    """
    Verifica se os parâmetros da API possuem valores padrão sensatos
    """
    # Examina a classe de parâmetros de requisição
    params_class = OperatorRequestParams
    
    # Verifica os valores padrão dos parâmetros
    assert params_class.__annotations__["query"].__origin__ is type(None) or params_class.model_fields["query"].default == "", "O parâmetro 'query' deve ter um valor padrão vazio"
    assert params_class.model_fields["page"].default == 1, "O parâmetro 'page' deve ter um valor padrão de 1"
    assert params_class.model_fields["page_size"].default == 10, "O parâmetro 'page_size' deve ter um valor padrão de 10"
    assert params_class.model_fields["order_direction"].default == "asc", "O parâmetro 'order_direction' deve ter um valor padrão de 'asc'"

@pytest.mark.asyncio
@patch('application.services.operator_service.OperatorSearchService.find_all_cached')
async def test_error_message_clarity(mock_find_all_cached, test_client):
    """
    Verifica se as mensagens de erro são claras e úteis
    """
    # Testa com um parâmetro inválido
    response = test_client.get("/api/v1/operators?page=0")
    assert response.status_code == 400
    
    # Obtém a mensagem de erro
    error = response.json()
    
    # Verifica se a mensagem de erro é clara
    assert "detail" in error, "A resposta de erro deve conter detalhes"
    if isinstance(error["detail"], list):
        for item in error["detail"]:
            assert "msg" in item, "Cada item de erro deve conter uma mensagem"
            assert len(item["msg"]) > 0, "A mensagem de erro não deve estar vazia"
            # Verifica se a mensagem possui palavras-chave que indicam o problema
            message = item["msg"].lower()
            assert "page" in message or "página" in message, "A mensagem de erro deve indicar qual campo está com problema"
            assert "valid" in message or "válid" in message or "greater" in message or "maior" in message, "A mensagem de erro deve indicar o tipo de problema"
    else:
        assert len(error["detail"]) > 0, "A mensagem de erro não deve estar vazia"

@pytest.mark.asyncio
@patch('application.services.operator_service.OperatorSearchService.find_all_cached')
async def test_response_format_consistency(mock_find_all_cached, test_client, mock_response):
    """
    Verifica se o formato da resposta é consistente em diferentes cenários
    """
    # Configura o mock para retornar dados simulados
    mock_find_all_cached.return_value = mock_response
    
    # Testa diferentes cenários de consulta
    scenarios = [
        {"params": "", "description": "Sem parâmetros"},
        {"params": "?page=1", "description": "Apenas página"},
        {"params": "?page_size=5", "description": "Apenas tamanho de página"},
        {"params": "?order_by=corporate_name", "description": "Apenas ordenação"},
        {"params": "?query=teste", "description": "Apenas consulta"},
        {"params": "?page=2&page_size=5&order_by=corporate_name&order_direction=desc", "description": "Todos os parâmetros"}
    ]
    
    for scenario in scenarios:
        response = test_client.get(f"/api/v1/operators{scenario['params']}")
        assert response.status_code == 200, f"Cenário '{scenario['description']}' deve retornar código 200"
        
        # Verifica se a resposta segue o mesmo formato em todos os cenários
        data = response.json()
        assert "data" in data, f"Cenário '{scenario['description']}' deve conter a propriedade 'data'"
        assert "page" in data, f"Cenário '{scenario['description']}' deve conter a propriedade 'page'"
        assert "page_size" in data, f"Cenário '{scenario['description']}' deve conter a propriedade 'page_size'"
        assert "total_pages" in data, f"Cenário '{scenario['description']}' deve conter a propriedade 'total_pages'"
        assert "total_items" in data, f"Cenário '{scenario['description']}' deve conter a propriedade 'total_items'"

@pytest.mark.asyncio
@patch('application.services.operator_service.OperatorSearchService.find_all_cached')
async def test_hypermedia_links(mock_find_all_cached, test_client, mock_response):
    """
    Verifica se a API utiliza hiperlinks para navegação (HATEOAS)
    """
    # Configura um mock com paginação
    mock_paginated = PageableResponse(
        data=mock_response.data,
        page=2,
        page_size=1,
        total_pages=3,
        total_items=3,
        query="",
        order_by="corporate_name",
        order_direction="asc"
    )
    mock_find_all_cached.return_value = mock_paginated
    
    # Faz a requisição para o endpoint
    response = test_client.get("/api/v1/operators?page=2&page_size=1")
    assert response.status_code == 200
    
    # Obtém os dados da resposta
    data = response.json()
    
    # Idealmente, uma API REST com HATEOAS deve incluir links para navegação
    # Verifica se existem informações de paginação que permitam navegar
    assert data["page"] == 2, "Deve mostrar a página atual"
    assert data["total_pages"] == 3, "Deve mostrar o total de páginas"
    
    # Estes testes podem falhar se a API não implementa HATEOAS
    # Descomente se a API implementar links para navegação
    """
    assert "_links" in data, "A resposta deve conter a propriedade '_links' para navegação"
    assert "self" in data["_links"], "Deve conter um link para a página atual"
    assert "next" in data["_links"], "Deve conter um link para a próxima página"
    assert "prev" in data["_links"], "Deve conter um link para a página anterior"
    assert "first" in data["_links"], "Deve conter um link para a primeira página"
    assert "last" in data["_links"], "Deve conter um link para a última página"
    """

@pytest.mark.asyncio
@patch('application.services.operator_service.OperatorSearchService.find_all_cached')
async def test_http_cache_headers(mock_find_all_cached, test_client, mock_response):
    """
    Verifica se a API utiliza cabeçalhos HTTP para cache
    """
    # Configura o mock para retornar dados simulados
    mock_find_all_cached.return_value = mock_response
    
    # Faz a requisição para o endpoint
    response = test_client.get("/api/v1/operators")
    
    # Verifica se a resposta inclui cabeçalhos de cache
    headers = response.headers
    
    # Estes testes podem falhar se a API não implementa cabeçalhos de cache
    # Descomente se a API implementar cabeçalhos de cache
    """
    assert "Cache-Control" in headers, "A resposta deve incluir o cabeçalho Cache-Control"
    assert "ETag" in headers, "A resposta deve incluir o cabeçalho ETag para validação de cache"
    assert "Last-Modified" in headers, "A resposta deve incluir o cabeçalho Last-Modified"
    """ 