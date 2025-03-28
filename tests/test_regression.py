import pytest
import json
import os
from datetime import datetime
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from presentation.main import create_application
from presentation.model.pageable_response import PageableResponse

# Diretório para armazenar os resultados de referência
REGRESSION_DIR = os.path.join(os.path.dirname(__file__), "regression_snapshots")
os.makedirs(REGRESSION_DIR, exist_ok=True)

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
        },
        {
            "id": 2,
            "operator_registry": "654321",
            "cnpj": "43210987654321",
            "corporate_name": "Empresa Teste 2",
            "trade_name": "Teste 2",
            "modality": "Seguradora",
            "city": "Rio de Janeiro",
            "state": "RJ"
        }
    ]
    
    return PageableResponse(
        data=mock_data,
        page=1,
        page_size=10,
        total_pages=1,
        total_items=2,
        query="",
        order_by="corporate_name",
        order_direction="asc"
    )

def save_snapshot(data, filename):
    """Salva um snapshot dos dados para testes de regressão futuros"""
    filepath = os.path.join(REGRESSION_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_snapshot(filename):
    """Carrega um snapshot salvo anteriormente"""
    filepath = os.path.join(REGRESSION_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

@pytest.mark.asyncio
@patch('application.services.operator_service.OperatorSearchService.find_all_cached')
async def test_api_response_structure_regression(mock_find_all_cached, test_client, mock_response):
    """
    Teste de regressão que verifica se a estrutura da resposta da API
    permanece consistente ao longo do tempo.
    """
    # Configura o mock para retornar dados simulados
    mock_find_all_cached.return_value = mock_response
    
    # Faz a requisição para o endpoint
    response = test_client.get("/api/v1/operators")
    assert response.status_code == 200
    
    # Obtém os dados da resposta
    current_data = response.json()
    
    # Nome do arquivo para o snapshot
    snapshot_file = "api_structure_snapshot.json"
    
    # Carrega o snapshot anterior, se existir
    reference_data = load_snapshot(snapshot_file)
    
    if reference_data is None:
        # Se não existir um snapshot anterior, cria um novo
        save_snapshot(current_data, snapshot_file)
        pytest.skip(f"Snapshot criado: {snapshot_file}. Execute o teste novamente para verificar regressões.")
    
    # Verifica se a estrutura da resposta permanece a mesma
    assert set(current_data.keys()) == set(reference_data.keys()), "A estrutura da resposta da API mudou"
    
    # Verifica se os tipos de dados dos campos permanecem os mesmos
    for key in current_data.keys():
        if key != "data":  # Ignora a verificação de tipo para os dados reais, verificamos apenas a estrutura
            assert type(current_data[key]) == type(reference_data[key]), f"O tipo de dados do campo '{key}' mudou"
    
    # Verifica a estrutura dos itens de dados (apenas o primeiro item, se disponível)
    if current_data["data"] and reference_data["data"]:
        current_item = current_data["data"][0]
        reference_item = reference_data["data"][0]
        assert set(current_item.keys()) == set(reference_item.keys()), "A estrutura dos itens de dados mudou"

@pytest.mark.asyncio
@patch('application.services.operator_service.OperatorSearchService.find_all_cached')
async def test_error_handling_regression(mock_find_all_cached, test_client):
    """
    Teste de regressão que verifica se o tratamento de erros permanece consistente.
    """
    # Configura o mock para lançar uma exceção
    mock_find_all_cached.side_effect = ValueError("Erro de teste proposital")
    
    # Faz a requisição para o endpoint
    response = test_client.get("/api/v1/operators")
    
    # Verifica se o código de status é 500 (erro interno do servidor)
    assert response.status_code == 500
    
    # Obtém os dados da resposta de erro
    current_error = response.json()
    
    # Nome do arquivo para o snapshot
    snapshot_file = "error_handling_snapshot.json"
    
    # Carrega o snapshot anterior, se existir
    reference_error = load_snapshot(snapshot_file)
    
    if reference_error is None:
        # Se não existir um snapshot anterior, cria um novo
        save_snapshot(current_error, snapshot_file)
        pytest.skip(f"Snapshot criado: {snapshot_file}. Execute o teste novamente para verificar regressões.")
    
    # Verifica se a estrutura da resposta de erro permanece a mesma
    assert set(current_error.keys()) == set(reference_error.keys()), "A estrutura da resposta de erro mudou"

@pytest.mark.asyncio
@patch('application.services.operator_service.OperatorSearchService.find_all_cached')
async def test_validation_error_response_regression(mock_find_all_cached, test_client):
    """
    Teste de regressão que verifica se as respostas de erro de validação permanecem consistentes.
    """
    # Faz a requisição para o endpoint com um parâmetro inválido
    response = test_client.get("/api/v1/operators?page=0")  # Página inválida (menor que 1)
    
    # Verifica se o código de status é 400 (requisição inválida)
    assert response.status_code == 400
    
    # Obtém os dados da resposta de erro de validação
    current_error = response.json()
    
    # Nome do arquivo para o snapshot
    snapshot_file = "validation_error_snapshot.json"
    
    # Carrega o snapshot anterior, se existir
    reference_error = load_snapshot(snapshot_file)
    
    if reference_error is None:
        # Se não existir um snapshot anterior, cria um novo
        save_snapshot(current_error, snapshot_file)
        pytest.skip(f"Snapshot criado: {snapshot_file}. Execute o teste novamente para verificar regressões.")
    
    # Verifica se a estrutura da resposta de erro de validação permanece a mesma
    assert set(current_error.keys()) == set(reference_error.keys()), "A estrutura da resposta de erro de validação mudou"
    
    # Verifica se a resposta contém detalhes sobre o erro
    assert "detail" in current_error, "A resposta de erro de validação não contém detalhes"

@pytest.mark.asyncio
@patch('application.services.operator_service.OperatorSearchService.find_all_cached')
async def test_pagination_regression(mock_find_all_cached, test_client, mock_response):
    """
    Teste de regressão que verifica se a paginação funciona consistentemente.
    """
    # Configura diferentes responses para diferentes páginas
    def mock_response_for_page(criteria):
        page = criteria.page
        page_size = criteria.page_size
        
        if page == 1:
            return mock_response
        elif page == 2:
            # Response para a página 2
            return PageableResponse(
                data=[{"id": 3, "corporate_name": "Empresa Teste 3"}],
                page=2,
                page_size=page_size,
                total_pages=2,
                total_items=3,
                query="",
                order_by="corporate_name",
                order_direction="asc"
            )
        return PageableResponse(
            data=[],
            page=page,
            page_size=page_size,
            total_pages=2,
            total_items=3,
            query="",
            order_by="corporate_name",
            order_direction="asc"
        )
    
    # Configura o mock para usar a função de resposta por página
    mock_find_all_cached.side_effect = mock_response_for_page
    
    # Testa a primeira página
    response1 = test_client.get("/api/v1/operators?page=1&page_size=2")
    assert response1.status_code == 200
    data1 = response1.json()
    
    # Testa a segunda página
    response2 = test_client.get("/api/v1/operators?page=2&page_size=2")
    assert response2.status_code == 200
    data2 = response2.json()
    
    # Verifica se as páginas são diferentes
    assert data1["page"] != data2["page"]
    
    # Verifica se os itens nas duas páginas são diferentes
    if data1["data"] and data2["data"]:
        ids_page1 = [item["id"] for item in data1["data"]]
        ids_page2 = [item["id"] for item in data2["data"]]
        assert not set(ids_page1).intersection(set(ids_page2)), "Itens duplicados encontrados em páginas diferentes"
    
    # Nome do arquivo para o snapshot de paginação
    snapshot_file = "pagination_snapshot.json"
    
    # Salva ambas as páginas em um objeto para o snapshot
    pagination_data = {
        "page1": data1,
        "page2": data2
    }
    
    # Carrega o snapshot anterior, se existir
    reference_data = load_snapshot(snapshot_file)
    
    if reference_data is None:
        # Se não existir um snapshot anterior, cria um novo
        save_snapshot(pagination_data, snapshot_file)
        pytest.skip(f"Snapshot criado: {snapshot_file}. Execute o teste novamente para verificar regressões.")
    
    # Verifica se a estrutura da paginação permanece a mesma
    assert set(pagination_data["page1"].keys()) == set(reference_data["page1"].keys()), "A estrutura da primeira página mudou"
    assert set(pagination_data["page2"].keys()) == set(reference_data["page2"].keys()), "A estrutura da segunda página mudou" 