import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from domain.repository.operator_repository import OperatorRepository
from application.services.operator_service import OperatorSearchService
from presentation.model.operator_request_params import OperatorRequestParams
from domain.model.operator import Operator

@pytest.fixture
def mock_db_session():
    # Mock para a sessão do banco de dados
    session_mock = MagicMock(spec=Session)
    return session_mock

@pytest.fixture
def mock_operators():
    # Mock para os operadores retornados pelo banco de dados
    operator1 = MagicMock(spec=Operator)
    operator1.id = 1
    operator1.corporate_name = "Empresa Teste 1"
    operator1.trade_name = "Teste 1"
    operator1.cnpj = "12345678901234"
    operator1.to_dict.return_value = {
        "id": 1,
        "operator_registry": "123456",
        "cnpj": "12345678901234",
        "corporate_name": "Empresa Teste 1",
        "trade_name": "Teste 1"
    }
    
    operator2 = MagicMock(spec=Operator)
    operator2.id = 2
    operator2.corporate_name = "Empresa Teste 2"
    operator2.trade_name = "Teste 2"
    operator2.cnpj = "43210987654321"
    operator2.to_dict.return_value = {
        "id": 2,
        "operator_registry": "654321",
        "cnpj": "43210987654321",
        "corporate_name": "Empresa Teste 2",
        "trade_name": "Teste 2"
    }
    
    return [operator1, operator2]

@pytest.fixture
def operator_repository(mock_db_session):
    # Cria uma instância do repositório de operadores
    return OperatorRepository(mock_db_session)

@pytest.fixture
def operator_service(operator_repository):
    # Cria uma instância do serviço de operadores
    return OperatorSearchService(operator_repository)

@pytest.mark.parametrize("query,expected_count", [
    ("", 2),  # Consulta vazia retorna todos os operadores
    ("Teste 1", 1),  # Consulta específica retorna apenas um operador
])
def test_repository_search_operators_integration(query, expected_count, operator_repository, mock_db_session, mock_operators):
    # Configura o mock da sessão para retornar os operadores mockados
    query_mock = MagicMock()
    query_mock.filter.return_value = query_mock
    query_mock.offset.return_value = query_mock
    query_mock.limit.return_value = query_mock
    
    if query == "Teste 1":
        query_mock.all.return_value = [mock_operators[0]]
        query_mock.with_entities.return_value.scalar.return_value = 1
    else:
        query_mock.all.return_value = mock_operators
        query_mock.with_entities.return_value.scalar.return_value = 1
    
    mock_db_session.query.return_value = query_mock
    
    # Cria os parâmetros de consulta
    params = OperatorRequestParams(
        query=query,
        page=1,
        page_size=10,
        order_by="corporate_name",
        order_direction="asc"
    )
    
    # Executa a função de busca
    operators, last_page = operator_repository.search_operators(params)
    
    # Verifica se o número de operadores retornados está correto
    assert len(operators) == expected_count
    
    # Verifica se o método query foi chamado com o modelo correto
    mock_db_session.query.assert_called_once()

@pytest.mark.asyncio
async def test_service_find_all_cached_integration(operator_service, operator_repository, mock_operators):
    # Configura o mock do repositório para retornar os operadores mockados
    operators_model = [MagicMock(id=op.id, to_dict=op.to_dict) for op in mock_operators]
    operator_repository.search_operators.return_value = (operators_model, 1)
    
    # Cria os parâmetros de consulta
    params = OperatorRequestParams(
        query="",
        page=1,
        page_size=10,
        order_by="corporate_name",
        order_direction="asc"
    )
    
    # Executa a função de busca com cache
    with patch('application.services.operator_service.Cache.REDIS'):
        with patch('application.services.operator_service.asyncio.get_running_loop'):
            response = await operator_service.find_all_cached(params)
    
    # Verifica se o serviço retornou o número correto de operadores
    assert len(response.data) == len(mock_operators)
    
    # Verifica se a função search_operators do repositório foi chamada com os parâmetros corretos
    operator_repository.search_operators.assert_called_once_with(params)

@pytest.mark.asyncio
async def test_full_integration_flow(mock_db_session, mock_operators):
    # Configura o mock da sessão para retornar os operadores mockados
    query_mock = MagicMock()
    query_mock.filter.return_value = query_mock
    query_mock.offset.return_value = query_mock
    query_mock.limit.return_value = query_mock
    query_mock.all.return_value = mock_operators
    query_mock.with_entities.return_value.scalar.return_value = 1
    
    mock_db_session.query.return_value = query_mock
    
    # Cria a cadeia de dependências
    repository = OperatorRepository(mock_db_session)
    service = OperatorSearchService(repository)
    
    # Cria os parâmetros de consulta
    params = OperatorRequestParams(
        query="",
        page=1,
        page_size=10,
        order_by="corporate_name",
        order_direction="asc"
    )
    
    # Executa o fluxo completo (find_all em vez de find_all_cached para simplificar o teste)
    response = service.find_all(params)
    
    # Verifica se a resposta tem os dados esperados
    assert response.page == 1
    assert response.page_size == 10
    assert response.total_pages == 1
    
    # Verifica se o método query foi chamado
    mock_db_session.query.assert_called_once() 