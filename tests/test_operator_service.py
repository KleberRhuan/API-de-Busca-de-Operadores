import datetime
import pytest
from typing import List, Dict, Any
from application.services.operator_service import search_operator, SearchResponse, ALLOWED_ORDER_COLUMNS
from domain.model.operator import Operator

# Sample row that simulates a database record
sample_db_row = {
    "id": 1,
    "registro_operadora": "REG001",
    "cnpj": "12345678901234",
    "razao_social": "Empresa Exemplo",
    "nome_fantasia": "Exemplo",
    "modalidade": "Type A",
    "logradouro": "Rua Exemplo",
    "numero": "123",
    "complemento": "Apto 1",
    "bairro": "Bairro Exemplo",
    "cidade": "Cidade Exemplo",
    "uf": "SP",
    "cep": "12345678",
    "ddd": "11",
    "telefone": "123456789",
    "fax": "987654321",
    "endereco_eletronico": "exemplo@empresa.com",
    "representante": "João Silva",
    "cargo_representante": "Gerente",
    "regiao_de_comercializacao": 1,
    "data_registro_ans": datetime.date(2023, 1, 1)
}

def fake_execute_query(
        sql: str,
        params: List[Any],
        fetch: bool = True
) -> List[Dict]:
    """
    Enhanced mock with type hints and clear parameter handling.
    
    This method provides:
    - Clear type information
    - Default fetch behavior
    - Flexible query handling
    """
    # Skip fetching if fetch is False
    if not fetch:
        return []

    # Simulate different query types
    if "SELECT *" in sql:
        return [sample_db_row]
    elif "SELECT COUNT(*)" in sql:
        return [{"total": 1}]

    return []

@pytest.fixture(autouse=True)
def patch_db_manager(monkeypatch):
    """
    Pytest fixture to patch the DBManager's execute_query method.
    
    This ensures consistent mocking of database queries across all tests.
    """
    from infra.db_manager import DBManager
    monkeypatch.setattr(DBManager, "execute_query", fake_execute_query)

def test_search_operator_success():
    """
    Test the search_operator function with a successful scenario.
    
    Verifies that:
    1. The response structure is correct
    2. Pagination parameters are preserved
    3. Results are correctly mapped to Operator objects
    """
    response = search_operator(
        query="Exemplo",
        page=1,
        page_size=10,
        order_by="razao_social",
        order_direction="asc"
    )

    # Verify response structure
    assert response.page == 1
    assert response.page_size == 10
    assert response.total_results == 1
    assert len(response.results) == 1

    # Verify Operator object mapping
    op: Operator = response.results[0]
    assert op.operator_registry == sample_db_row["registro_operadora"]
    assert op.corporate_name == sample_db_row["razao_social"]
    assert op.registration_date == sample_db_row["data_registro_ans"]

def test_search_operator_invalid_order_by():
    """
    Test the search_operator function with an invalid order_by column.
    
    Ensures that:
    1. A ValueError is raised for invalid order columns
    2. The error message provides clear guidance
    """
    with pytest.raises(ValueError) as excinfo:
        search_operator(
            query="Exemplo",
            page=1,
            page_size=10,
            order_by="invalid_column",
            order_direction="asc"
        )

    assert "Invalid order_by property" in str(excinfo.value)