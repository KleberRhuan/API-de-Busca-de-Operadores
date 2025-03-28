import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from presentation.main import create_application
from domain.model.operator import Operator
from presentation.model.pageable_response import PageableResponse

@pytest.fixture
def test_client():
    # Cria uma instância do aplicativo FastAPI para testes
    app = create_application()
    return TestClient(app)

@pytest.fixture
def mock_operator_data():
    # Dados mockados para simular resultados do banco de dados
    return [
        {
            "id": 1,
            "operator_registry": "123456",
            "cnpj": "12345678901234",
            "corporate_name": "Empresa Teste 1",
            "trade_name": "Teste 1",
            "modality": "Cooperativa Médica",
            "street": "Rua Teste",
            "number": "123",
            "complement": "Sala 1",
            "neighborhood": "Centro",
            "city": "São Paulo",
            "state": "SP",
            "zip": "01234567",
            "area_code": "11",
            "phone": "12345678",
            "fax": "12345678",
            "email": "teste@teste.com",
            "representative": "João Silva",
            "representative_position": "Diretor",
            "sales_region": "Nacional",
            "registration_date": "2020-01-01"
        },
        {
            "id": 2,
            "operator_registry": "654321",
            "cnpj": "43210987654321",
            "corporate_name": "Empresa Teste 2",
            "trade_name": "Teste 2",
            "modality": "Seguradora",
            "street": "Av. Teste",
            "number": "456",
            "complement": "Andar 10",
            "neighborhood": "Jardins",
            "city": "Rio de Janeiro",
            "state": "RJ",
            "zip": "76543210",
            "area_code": "21",
            "phone": "87654321",
            "fax": "87654321",
            "email": "teste2@teste.com",
            "representative": "Maria Silva",
            "representative_position": "Presidente",
            "sales_region": "Sudeste",
            "registration_date": "2019-05-10"
        }
    ]

@pytest.mark.asyncio
@patch('application.services.operator_service.OperatorSearchService.find_all_cached')
async def test_search_operators_endpoint_success(mock_find_all_cached, test_client, mock_operator_data):
    # Configura o mock para retornar dados simulados
    mock_response = PageableResponse(
        data=mock_operator_data,
        page=1,
        page_size=10,
        total_pages=1,
        total_items=2,
        query="",
        order_by="corporate_name",
        order_direction="asc"
    )
    mock_find_all_cached.return_value = mock_response
    
    # Faz a requisição para o endpoint
    response = test_client.get("/api/v1/operators")
    
    # Verifica se a resposta é bem-sucedida
    assert response.status_code == 200
    
    # Verifica os dados da resposta
    response_data = response.json()
    assert response_data["page"] == 1
    assert response_data["page_size"] == 10
    assert response_data["total_pages"] == 1
    assert response_data["total_items"] == 2
    assert len(response_data["data"]) == 2
    assert response_data["data"][0]["corporate_name"] == "Empresa Teste 1"
    assert response_data["data"][1]["corporate_name"] == "Empresa Teste 2"

@pytest.mark.asyncio
@patch('application.services.operator_service.OperatorSearchService.find_all_cached')
async def test_search_operators_with_query_param(mock_find_all_cached, test_client, mock_operator_data):
    # Configura o mock para retornar dados filtrados simulados
    mock_response = PageableResponse(
        data=[mock_operator_data[0]],  # Apenas o primeiro resultado
        page=1,
        page_size=10,
        total_pages=1,
        total_items=1,
        query="Teste 1",
        order_by="corporate_name",
        order_direction="asc"
    )
    mock_find_all_cached.return_value = mock_response
    
    # Faz a requisição para o endpoint com parâmetro de consulta
    response = test_client.get("/api/v1/operators?query=Teste+1")
    
    # Verifica se a resposta é bem-sucedida
    assert response.status_code == 200
    
    # Verifica os dados da resposta
    response_data = response.json()
    assert response_data["page"] == 1
    assert response_data["total_items"] == 1
    assert len(response_data["data"]) == 1
    assert response_data["data"][0]["trade_name"] == "Teste 1"

@pytest.mark.asyncio
@patch('application.services.operator_service.OperatorSearchService.find_all_cached')
async def test_search_operators_with_pagination(mock_find_all_cached, test_client, mock_operator_data):
    # Configura o mock para retornar dados paginados simulados
    mock_response = PageableResponse(
        data=[mock_operator_data[1]],  # Apenas o segundo resultado
        page=2,
        page_size=1,
        total_pages=2,
        total_items=2,
        query="",
        order_by="corporate_name",
        order_direction="asc"
    )
    mock_find_all_cached.return_value = mock_response
    
    # Faz a requisição para o endpoint com parâmetros de paginação
    response = test_client.get("/api/v1/operators?page=2&page_size=1")
    
    # Verifica se a resposta é bem-sucedida
    assert response.status_code == 200
    
    # Verifica os dados da resposta
    response_data = response.json()
    assert response_data["page"] == 2
    assert response_data["page_size"] == 1
    assert response_data["total_pages"] == 2
    assert len(response_data["data"]) == 1
    assert response_data["data"][0]["trade_name"] == "Teste 2"

@pytest.mark.asyncio
@patch('application.services.operator_service.OperatorSearchService.find_all_cached')
async def test_search_operators_with_ordering(mock_find_all_cached, test_client, mock_operator_data):
    # Configura o mock para retornar dados ordenados simulados
    mock_response = PageableResponse(
        data=[mock_operator_data[1], mock_operator_data[0]],  # Ordem invertida
        page=1,
        page_size=10,
        total_pages=1,
        total_items=2,
        query="",
        order_by="corporate_name",
        order_direction="desc"
    )
    mock_find_all_cached.return_value = mock_response
    
    # Faz a requisição para o endpoint com parâmetros de ordenação
    response = test_client.get("/api/v1/operators?order_by=corporate_name&order_direction=desc")
    
    # Verifica se a resposta é bem-sucedida
    assert response.status_code == 200
    
    # Verifica os dados da resposta
    response_data = response.json()
    assert response_data["order_by"] == "corporate_name"
    assert response_data["order_direction"] == "desc"
    assert len(response_data["data"]) == 2
    assert response_data["data"][0]["corporate_name"] == "Empresa Teste 2"
    assert response_data["data"][1]["corporate_name"] == "Empresa Teste 1" 