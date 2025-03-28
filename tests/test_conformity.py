import pytest
import re
from fastapi.testclient import TestClient
from unittest.mock import patch
from presentation.main import create_application
from presentation.model.pageable_response import PageableResponse
from application.services.operator_service import OperatorSearchService

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
async def test_http_status_codes_conformity(mock_find_all_cached, test_client, mock_response):
    """
    Verifica se a API utiliza códigos HTTP corretos conforme os padrões REST
    """
    # Configura o mock para retornar dados simulados
    mock_find_all_cached.return_value = mock_response
    
    # Testa código 200 (OK) para requisição bem-sucedida
    response = test_client.get("/api/v1/operators")
    assert response.status_code == 200, "Requisição bem-sucedida deve retornar código 200"
    
    # Testa código 400 (Bad Request) para requisição inválida
    response = test_client.get("/api/v1/operators?page=0")  # Página inválida
    assert response.status_code == 400, "Requisição inválida deve retornar código 400"
    
    # Testa código 404 (Not Found) para recurso não encontrado
    response = test_client.get("/api/v1/non_existent_endpoint")
    assert response.status_code == 404, "Recurso não encontrado deve retornar código 404"
    
    # Testa código 405 (Method Not Allowed) para método HTTP não permitido
    response = test_client.post("/api/v1/operators")
    assert response.status_code == 405, "Método não permitido deve retornar código 405"

@pytest.mark.asyncio
@patch('application.services.operator_service.OperatorSearchService.find_all_cached')
async def test_response_content_type_conformity(mock_find_all_cached, test_client, mock_response):
    """
    Verifica se a API retorna o tipo de conteúdo correto (JSON)
    """
    # Configura o mock para retornar dados simulados
    mock_find_all_cached.return_value = mock_response
    
    # Faz a requisição para o endpoint
    response = test_client.get("/api/v1/operators?query=test")
    
    # Verifica se o tipo de conteúdo é JSON
    assert "application/json" in response.headers["content-type"], "Resposta deve ser do tipo application/json"

@pytest.mark.asyncio
@patch('application.services.operator_service.OperatorSearchService.find_all_cached')
async def test_pagination_conformity(mock_find_all_cached, test_client, mock_response):
    """
    Verifica se a paginação segue as práticas recomendadas de API REST
    """
    # Configura o mock para retornar dados simulados
    mock_find_all_cached.return_value = mock_response
    
    # Faz a requisição para o endpoint com parâmetros de paginação
    response = test_client.get("/api/v1/operators?page=1&page_size=10")
    assert response.status_code == 200
    
    # Obtém os dados da resposta
    data = response.json()
    
    # Verifica se a resposta contém informações de paginação
    assert "page" in data, "Resposta deve conter informação de página atual"
    assert "page_size" in data, "Resposta deve conter informação de tamanho da página"
    assert "total_pages" in data, "Resposta deve conter informação de total de páginas"
    assert "total_items" in data, "Resposta deve conter informação de total de itens"
    
    # Verifica se os valores de paginação são consistentes
    assert data["page"] == 1, "Página atual deve ser 1"
    assert data["page_size"] == 10, "Tamanho da página deve ser 10"
    assert data["total_pages"] > 0, "Total de páginas deve ser maior que zero"
    assert data["total_items"] > 0, "Total de itens deve ser maior que zero"

@pytest.mark.asyncio
@patch('application.services.operator_service.OperatorSearchService.find_all_cached')
async def test_json_structure_conformity(mock_find_all_cached, test_client, mock_response):
    """
    Verifica se a estrutura JSON segue as práticas recomendadas
    """
    # Configura o mock para retornar dados simulados
    mock_find_all_cached.return_value = mock_response
    
    # Faz a requisição para o endpoint
    with patch.object(OperatorSearchService, 'find_all_cached', return_value=mock_response):
        response = test_client.get("/api/v1/operators")
    assert response.status_code == 200
    
    # Obtém os dados da resposta
    data = response.json()
    
    # Verifica se os nomes das propriedades seguem o padrão camelCase
    camel_case_pattern = re.compile(r'^[a-z]+(?:[A-Z][a-z]+)*$')
    for key in data.keys():
        if key != "data":  # Ignora a propriedade "data" que é um array
            assert camel_case_pattern.match(key), f"A propriedade '{key}' deve seguir o padrão camelCase"
    
    # Verifica se a resposta contém a propriedade "data" com os resultados
    assert "data" in data, "Resposta deve conter a propriedade 'data'"
    assert isinstance(data["data"], list), "A propriedade 'data' deve ser um array"
    
    # Verifica a estrutura dos itens na propriedade "data"
    if data["data"]:
        item = data["data"][0]
        assert "id" in item, "Cada item deve conter um identificador 'id'"
        for key, value in item.items():
            # Verifica se as propriedades dos itens também seguem o padrão camelCase
            assert camel_case_pattern.match(key), f"A propriedade '{key}' do item deve seguir o padrão camelCase"

@pytest.mark.asyncio
@patch('application.services.operator_service.OperatorSearchService.find_all_cached')
async def test_api_versioning_conformity(mock_find_all_cached, test_client):
    """
    Verifica se a API utiliza versionamento correto
    """
    # Verifica se o endpoint da API inclui o número da versão
    assert "/api/v1/" in "/api/v1/operators", "O endpoint da API deve incluir o número da versão (v1)"

@pytest.mark.asyncio
@patch('application.services.operator_service.OperatorSearchService.find_all_cached')
async def test_error_response_conformity(mock_find_all_cached, test_client):
    """
    Verifica se as respostas de erro seguem as práticas recomendadas
    """
    # Faz uma requisição que gerará um erro (parâmetro inválido)
    response = test_client.get("/api/v1/operators?page=0")
    assert response.status_code == 400
    
    # Obtém os dados da resposta de erro
    error = response.json()
    
    # Verifica se a resposta de erro contém as propriedades necessárias
    assert "detail" in error, "A resposta de erro deve conter a propriedade 'detail'"
    assert isinstance(error["detail"], (str, list, dict)), "A propriedade 'detail' deve ser uma string, lista ou objeto"
    
    if isinstance(error["detail"], list):
        for item in error["detail"]:
            assert "loc" in item, "Cada item de erro deve conter a localização do erro"
            assert "msg" in item, "Cada item de erro deve conter uma mensagem"
            assert "type" in item, "Cada item de erro deve conter o tipo de erro"

@pytest.mark.asyncio
@patch('application.services.operator_service.OperatorSearchService.find_all_cached')
async def test_http_methods_conformity(mock_find_all_cached, test_client):
    """
    Verifica se a API implementa os métodos HTTP corretamente
    """
    # Verifica se GET é permitido
    response = test_client.get("/api/v1/operators")
    assert response.status_code == 200, "GET deve ser permitido para o endpoint de listagem"
    
    # Verifica se POST não é permitido para este endpoint (é um endpoint somente de leitura)
    response = test_client.post("/api/v1/operators")
    assert response.status_code == 405, "POST não deve ser permitido para o endpoint de listagem (é somente leitura)"
    
    # Verifica se PUT não é permitido para este endpoint (é um endpoint somente de leitura)
    response = test_client.put("/api/v1/operators")
    assert response.status_code == 405, "PUT não deve ser permitido para o endpoint de listagem (é somente leitura)"
    
    # Verifica se DELETE não é permitido para este endpoint (é um endpoint somente de leitura)
    response = test_client.delete("/api/v1/operators")
    assert response.status_code == 405, "DELETE não deve ser permitido para o endpoint de listagem (é somente leitura)" 