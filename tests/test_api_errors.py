import pytest
from fastapi.testclient import TestClient
from presentation.main import app

client = TestClient(app)


def test_method_not_allowed():
    response = client.post("/api/v1/operators")  # POST is not allowed
    assert response.status_code == 405
    data = response.json()
    assert data["status"] == 405
    assert data["type"] == "/metodo-invalido"
    assert data["title"] == "Método Inválido"
    assert "Método não permitido" in data["userMessage"]


def test_resource_not_found():
    response = client.get("/api/v1/non-existent-route")
    assert response.status_code == 404
    data = response.json()
    assert data["status"] == 404
    assert data["type"] == "/recurso-nao-encontrado"
    assert data["title"] == "Recurso Não Encontrado"
    assert "não existe" in data["userMessage"]


def test_validation_error():
    response = client.get("/api/v1/operators", params={"page": 0})  # page < 1 is invalid
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == 422
    assert data["type"] == "/mensagem-incompreensivel"
    assert data["title"] == "Mensagem Incompreensível"
    assert "inválidos" in data["userMessage"]
    assert isinstance(data["violations"], list)


def test_generic_error(monkeypatch):
    # Simula erro interno no search_operator
    from application import services

    def raise_error(*args, **kwargs):
        raise Exception("Erro inesperado simulado")

    monkeypatch.setattr(services.operator_service, "search_operator", raise_error)

    response = client.get("/api/v1/operators", params={"query": "abc"})
    assert response.status_code == 500
    data = response.json()
    assert data["status"] == 500
    assert data["type"] == "/erro-interno"
    assert data["title"] == "Erro Interno do Sistema"
    assert "servidor" in data["userMessage"]
