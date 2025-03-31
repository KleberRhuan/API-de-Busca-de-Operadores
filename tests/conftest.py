import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from limits.storage import MemoryStorage

from src.presentation.main import create_application

# Configuração de ambiente para testes
os.environ["ENV"] = "test"
os.environ["RATE_LIMIT"] = "10"
os.environ["RATE_WINDOW"] = "10"

# Fixtures comuns para os testes


@pytest.fixture
def test_app():
    """Fornece uma instância da aplicação para testes"""
    return create_application()


@pytest.fixture
def client():
    """Cliente de teste configurado para a aplicação FastAPI"""
    from starlette.middleware.base import BaseHTTPMiddleware

    # Desativar rate limiting para evitar falhas nos testes
    from src.infra.middleware.rate_limit_middleware import RateLimitMiddleware
    from src.presentation.main import application

    # Remover o middleware de rate limit se existir
    middlewares_to_keep = []
    for middleware in application.user_middleware:
        if not isinstance(middleware.cls, type) or not issubclass(
            middleware.cls, RateLimitMiddleware
        ):
            middlewares_to_keep.append(middleware)

    application.user_middleware = middlewares_to_keep
    # Reconstruir o stack de middlewares
    application.middleware_stack = application.build_middleware_stack()

    with TestClient(application) as test_client:
        yield test_client


@pytest.fixture
def mock_redis():
    """Fornece um mock para o Redis"""
    with patch("src.infra.database.get_redis_connection") as mock:
        mock_redis = MagicMock()
        mock.return_value = mock_redis
        yield mock_redis


@pytest.fixture
def mock_memory_storage():
    """Fornece um mock para o MemoryStorage usado no rate limiting"""
    storage = MemoryStorage()
    return storage


@pytest.fixture
def mock_operator_service(client):
    """Fornece um mock para o serviço de operadoras"""
    from src.presentation.api.routes import get_operator_service

    mock_service = AsyncMock()
    original_dependency = client.app.dependency_overrides.get(
        get_operator_service, get_operator_service
    )

    # Substituir a dependência por um mock
    client.app.dependency_overrides[get_operator_service] = lambda: mock_service

    yield mock_service

    # Restaurar a dependência original
    if original_dependency == get_operator_service:
        client.app.dependency_overrides.pop(get_operator_service, None)
    else:
        client.app.dependency_overrides[get_operator_service] = original_dependency


@pytest.fixture
def configure_service_mocks(mock_operator_service):
    """Configura mocks para retornar respostas no formato correto durante os testes"""

    def _configure_empty_response(*args, **kwargs):
        return {
            "data": [],
            "page": 1,
            "pageSize": 10,
            "totalItems": 0,
            "totalPages": 0,
            "search": "",
            "sortField": None,
            "sortDirection": "asc",
        }

    # Configura o serviço para retornar uma resposta vazia formatada corretamente
    mock_operator_service.find_all_cached.return_value = _configure_empty_response()

    return mock_operator_service


# Dados de exemplo para uso nos testes
@pytest.fixture
def sample_operators():
    """Fornece uma lista de operadoras de exemplo para testes"""
    return [
        {
            "operator_registry": "123456",
            "cnpj": "12.345.678/0001-00",
            "corporate_name": "OPERADORA TESTE 1 LTDA",
            "trade_name": "OPERADORA TESTE 1",
            "modality": "Medicina de Grupo",
            "street": "Rua Teste",
            "number": "123",
            "complement": "Sala 1",
            "neighborhood": "Centro",
            "city": "São Paulo",
            "state": "SP",
            "zip": "01234-567",
            "area_code": "11",
            "phone": "1234-5678",
            "fax": "1234-5679",
            "email": "contato@operadora1.com.br",
            "representative": "João da Silva",
            "representative_position": "Diretor",
            "sales_region": 1,
        },
        {
            "operator_registry": "654321",
            "cnpj": "98.765.432/0001-00",
            "corporate_name": "OPERADORA TESTE 2 LTDA",
            "trade_name": "OPERADORA TESTE 2",
            "modality": "Cooperativa Médica",
            "street": "Av. Teste",
            "number": "456",
            "complement": None,
            "neighborhood": "Jardim",
            "city": "Rio de Janeiro",
            "state": "RJ",
            "zip": "98765-432",
            "area_code": "21",
            "phone": "9876-5432",
            "fax": None,
            "email": "contato@operadora2.com.br",
            "representative": "Maria Souza",
            "representative_position": "Presidente",
            "sales_region": 2,
        },
    ]


@pytest.fixture
def paginated_operators_response(sample_operators):
    """Fornece uma resposta paginada de operadoras para testes"""
    return {
        "data": sample_operators,
        "page": 1,
        "pageSize": 10,
        "totalItems": 2,
        "totalPages": 1,
        "search": "operadora",
        "sortField": None,
        "sortDirection": "asc",
    }
