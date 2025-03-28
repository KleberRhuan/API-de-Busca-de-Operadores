import pytest
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from presentation.main import create_application
from presentation.model.pageable_response import PageableResponse

@pytest.fixture
def test_client():
    app = create_application()
    return TestClient(app)

@pytest.fixture
def mock_response():
    # Dados mockados para simular resultados do banco de dados
    mock_data = []
    for i in range(100):
        mock_data.append({
            "id": i,
            "operator_registry": f"REG{i}",
            "cnpj": f"1234567890{i:04d}",
            "corporate_name": f"Empresa Teste {i}",
            "trade_name": f"Teste {i}",
            "modality": "Cooperativa Médica",
            "city": "São Paulo",
            "state": "SP"
        })
    
    return PageableResponse(
        data=mock_data,
        page=1,
        page_size=100,
        total_pages=1,
        total_items=100,
        query="",
        order_by="corporate_name",
        order_direction="asc"
    )

@pytest.mark.asyncio
@patch('application.services.operator_service.OperatorSearchService.find_all_cached')
async def test_response_time_single_request(mock_find_all_cached, test_client, mock_response):
    # Configura o mock para retornar dados simulados
    mock_find_all_cached.return_value = mock_response
    
    # Mede o tempo de resposta para uma única requisição
    start_time = time.time()
    response = test_client.get("/api/v1/operators")
    end_time = time.time()
    
    # Verifica se a resposta é bem-sucedida
    assert response.status_code == 200
    
    # Verifica se o tempo de resposta está dentro do limite aceitável (500ms)
    response_time = end_time - start_time
    assert response_time < 0.5, f"Tempo de resposta muito alto: {response_time:.2f}s"
    
    print(f"Tempo de resposta para uma requisição: {response_time:.4f}s")

@pytest.mark.asyncio
@patch('application.services.operator_service.OperatorSearchService.find_all_cached')
async def test_concurrent_requests_performance(mock_find_all_cached, test_client, mock_response):
    # Configura o mock para retornar dados simulados
    mock_find_all_cached.return_value = mock_response
    
    num_requests = 50
    
    async def make_request():
        return test_client.get("/api/v1/operators")
    
    # Executa requisições concorrentes
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=10) as executor:
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(executor, make_request) for _ in range(num_requests)]
        responses = await asyncio.gather(*tasks)
    end_time = time.time()
    
    # Verifica se todas as respostas são bem-sucedidas
    for response in responses:
        assert response.status_code == 200
    
    # Calcula o tempo médio por requisição
    total_time = end_time - start_time
    avg_time = total_time / num_requests
    
    # Calcula requisições por segundo
    rps = num_requests / total_time
    
    # Verifica se o tempo médio está dentro do limite aceitável (100ms por requisição)
    assert avg_time < 0.1, f"Tempo médio por requisição muito alto: {avg_time:.4f}s"
    
    print(f"Resultados para {num_requests} requisições concorrentes:")
    print(f"Tempo total: {total_time:.2f}s")
    print(f"Tempo médio por requisição: {avg_time:.4f}s")
    print(f"Requisições por segundo: {rps:.2f}")

@pytest.mark.asyncio
@patch('application.services.operator_service.OperatorSearchService.find_all_cached')
async def test_response_time_with_filtering(mock_find_all_cached, test_client, mock_response):
    # Configura o mock para retornar dados simulados
    mock_find_all_cached.return_value = mock_response
    
    # Lista de diferentes consultas para testar
    queries = [
        "",  # Sem filtro
        "teste",  # Filtro simples
        "empresa teste 50",  # Filtro mais específico
        "inexistente"  # Filtro que não encontra resultados
    ]
    
    # Testa o tempo de resposta para cada consulta
    for query in queries:
        start_time = time.time()
        response = test_client.get(f"/api/v1/operators?query={query}")
        end_time = time.time()
        
        # Verifica se a resposta é bem-sucedida
        assert response.status_code == 200
        
        # Calcula o tempo de resposta
        response_time = end_time - start_time
        
        # Verifica se o tempo de resposta está dentro do limite aceitável (1s)
        assert response_time < 1.0, f"Tempo de resposta muito alto para query '{query}': {response_time:.2f}s"
        
        print(f"Tempo de resposta para query '{query}': {response_time:.4f}s")

@pytest.mark.asyncio
@patch('application.services.operator_service.OperatorSearchService.find_all_cached')
async def test_response_time_with_pagination(mock_find_all_cached, test_client, mock_response):
    # Configura o mock para retornar dados simulados
    mock_find_all_cached.return_value = mock_response
    
    # Testa diferentes configurações de paginação
    pagination_configs = [
        {"page": 1, "page_size": 10},
        {"page": 2, "page_size": 20},
        {"page": 5, "page_size": 50},
        {"page": 10, "page_size": 100}
    ]
    
    # Testa o tempo de resposta para cada configuração de paginação
    for config in pagination_configs:
        start_time = time.time()
        response = test_client.get(f"/api/v1/operators?page={config['page']}&page_size={config['page_size']}")
        end_time = time.time()
        
        # Verifica se a resposta é bem-sucedida
        assert response.status_code == 200
        
        # Calcula o tempo de resposta
        response_time = end_time - start_time
        
        # Verifica se o tempo de resposta está dentro do limite aceitável (1s)
        assert response_time < 1.0, f"Tempo de resposta muito alto para paginação page={config['page']}, page_size={config['page_size']}: {response_time:.2f}s"
        
        print(f"Tempo de resposta para paginação page={config['page']}, page_size={config['page_size']}: {response_time:.4f}s") 