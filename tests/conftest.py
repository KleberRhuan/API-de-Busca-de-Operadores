import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from src.presentation.main import create_application
from src.infra.database import get_redis_connection
from limits.storage import MemoryStorage

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
def client(test_app):
    """Fornece um cliente de teste para a API"""
    return TestClient(test_app)

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
def mock_operator_service():
    """Fornece um mock para o serviço de operadoras"""
    with patch("src.application.service.operator_service.OperatorService") as mock:
        mock_service = MagicMock()
        mock.return_value = mock_service
        yield mock_service

# Dados de exemplo para uso nos testes
@pytest.fixture
def sample_operators():
    """Fornece uma lista de operadoras de exemplo para testes"""
    return [
        {
            "id": 1,
            "registro_ans": "123456",
            "cnpj": "12.345.678/0001-00",
            "razao_social": "OPERADORA TESTE 1 LTDA",
            "nome_fantasia": "OPERADORA TESTE 1",
            "modalidade": "Medicina de Grupo",
            "logradouro": "Rua Teste",
            "numero": "123",
            "complemento": "Sala 1",
            "bairro": "Centro",
            "cidade": "São Paulo",
            "uf": "SP",
            "cep": "01234-567",
            "ddd": "11",
            "telefone": "1234-5678",
            "fax": "1234-5679",
            "email": "contato@operadora1.com.br",
            "representante": "João da Silva",
            "cargo_representante": "Diretor",
            "data_registro_ans": "2020-01-01"
        },
        {
            "id": 2,
            "registro_ans": "654321",
            "cnpj": "98.765.432/0001-00",
            "razao_social": "OPERADORA TESTE 2 LTDA",
            "nome_fantasia": "OPERADORA TESTE 2",
            "modalidade": "Cooperativa Médica",
            "logradouro": "Av. Teste",
            "numero": "456",
            "complemento": None,
            "bairro": "Jardim",
            "cidade": "Rio de Janeiro",
            "uf": "RJ",
            "cep": "98765-432",
            "ddd": "21",
            "telefone": "9876-5432",
            "fax": None,
            "email": "contato@operadora2.com.br",
            "representante": "Maria Souza",
            "cargo_representante": "Presidente",
            "data_registro_ans": "2019-05-15"
        }
    ]

@pytest.fixture
def paginated_operators_response(sample_operators):
    """Fornece uma resposta paginada de operadoras para testes"""
    return {
        "content": sample_operators,
        "page": 1,
        "page_size": 10,
        "total_elements": 2,
        "total_pages": 1
    } 