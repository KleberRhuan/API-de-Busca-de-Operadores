# tests/test_api.py
import datetime
import pytest
from fastapi.testclient import TestClient
from presentation.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def patch_search_operator(monkeypatch):
    from application.services.operator_service import SearchResponse
    from domain.model.operator import Operator
    import datetime

    def fake_search_operator(query, page, page_size, order_by, order_direction):
        op = Operator(
            id=1,
            operator_registry="REG001",
            tax_identifier="12345678901234",
            corporate_name="Empresa Exemplo",
            trade_name="Exemplo",
            modality="Type A",
            street="Rua Exemplo",
            number="123",
            complement="Apto 1",
            neighborhood="Bairro Exemplo",
            city="Cidade Exemplo",
            state="SP",
            zip="12345678",
            area_code="11",
            phone="123456789",
            fax="987654321",
            email_address="exemplo@empresa.com",
            representative="João Silva",
            representative_position="Gerente",
            sales_region=1,
            registration_date=datetime.date(2023, 1, 1)
        )
        return SearchResponse(page=page, page_size=page_size, total_results=1, results=[op])

    # Patch the search_operator function in the presentation layer.
    monkeypatch.setattr("presentation.main.search_operator", fake_search_operator)

def test_api_success():
    response = client.get(
        "/api/v1/operators",
        params={
            "query": "Exemplo",
            "page": 1,
            "page_size": 10,
            "order_by": "razao_social",
            "order_direction": "asc"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total_results"] == 1
    assert isinstance(data["results"], list)
    assert data["results"][0]["operator_registry"] == "REG001"

def test_api_invalid_order_by():
    response = client.get(
        "/api/v1/operators",
        params={
            "query": "Exemplo",
            "page": 1,
            "page_size": 10,
            "order_by": "invalid_column",
            "order_direction": "asc"
        }
    )
    # The invalid order_by parameter should cause our endpoint to raise a 500 error,
    # as our service function raises a ValueError.
    assert response.status_code == 500
    data = response.json()
    assert "Invalid order_by property" in data["detail"]

def test_api_unexpected_query_param():
    # If your endpoint were set up to restrict extra query parameters, then you could test that.
    # In our current implementation, we don't check for extra params so this test will succeed.
    response = client.get(
        "/api/v1/operators",
        params={
            "query": "Exemplo",
            "page": 1,
            "page_size": 10,
            "order_by": "razao_social",
            "order_direction": "asc",
            "unexpected": "param"
        }
    )
    # Since our endpoint doesn't enforce restrictions on extra query params, we expect a 200.
    assert response.status_code == 200