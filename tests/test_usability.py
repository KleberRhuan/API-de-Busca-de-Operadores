import json

import pytest
from fastapi import status


class TestApiUsability:
    """Testes para verificar a usabilidade da API"""

    def test_error_messages_clarity(self, client):
        """Teste para verificar a clareza das mensagens de erro"""
        # Testar erro de validação (search muito curta)
        response = client.get("/api/v1/operators?search=a")

        # Verificar se a resposta tem o status de erro de validação
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Verificar a estrutura da resposta de erro
        error_response = response.json()
        assert "type" in error_response
        assert "title" in error_response
        assert "detail" in error_response
        assert "violations" in error_response

        # Verificar se as violações são detalhadas
        assert len(error_response["violations"]) > 0
        for violation in error_response["violations"]:
            assert "name" in violation
            assert "message" in violation

        # Verificar se existe uma violação relacionada ao parâmetro search
        assert any(
            violation["name"] == "search" for violation in error_response["violations"]
        )

    def test_pagination_usability(self, client, mock_operator_service):
        """Teste para verificar a usabilidade da paginação"""
        # Configurar uma resposta paginada
        mock_response = {
            "data": [
                {"id": i, "nome_fantasia": f"Operadora {i}"} for i in range(1, 11)
            ],
            "page": 2,
            "page_size": 10,
            "total_items": 25,
            "total_pages": 3,
            "search": "teste",
            "sort_field": None,
            "sort_direction": "asc",
        }
        mock_operator_service.find_all_cached.return_value = mock_response

        # Fazer a requisição para a página 2
        response = client.get("/api/v1/operators?search=teste&page=2&page_size=10")

        # Verificar a resposta
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verificar elementos necessários para boa usabilidade de paginação
        assert "page" in data
        assert "pageSize" in data
        assert "totalItems" in data
        assert "totalPages" in data

        # Verificar valores de paginação
        assert data["page"] == 2
        assert data["pageSize"] == 10
        assert data["totalItems"] == 25
        assert data["totalPages"] == 3

    def test_invalid_parameters_handling(self, client):
        """Teste para verificar o tratamento de parâmetros inválidos"""
        # Testar vários cenários de parâmetros inválidos
        invalid_params = [
            # Página negativa
            {"search": "teste", "page": -1},
            # Tamanho de página zero
            {"search": "teste", "pageSize": 0},
            # Tamanho de página maior que o permitido
            {"search": "teste", "pageSize": 1000},
            # Parâmetro de ordenação inválido
            {"search": "teste", "sortField": "campo_inexistente"},
            # Direção de ordenação inválida
            {"search": "teste", "sortDirection": "invalid"},
        ]

        for params in invalid_params:
            # Construir a string de search
            search_string = "&".join(
                [f"{key}={value}" for key, value in params.items()]
            )

            # Fazer a requisição
            response = client.get(f"/api/v1/operators?{search_string}")

            # Verificar se a resposta é um erro de validação
            assert (
                response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            ), f"Parâmetros inválidos não geraram erro de validação: {params}"

            # Verificar a estrutura da resposta de erro
            error_response = response.json()
            assert "violations" in error_response
            assert len(error_response["violations"]) > 0

    def test_consistent_error_format(self, client, mock_operator_service):
        """Teste para verificar a consistência do formato de erro em diferentes situações"""
        # Lista de erros a testar
        error_scenarios = [
            # Erro de validação
            {
                "request": lambda c: c.get("/api/v1/operators?search=a"),
                "expected_status": status.HTTP_422_UNPROCESSABLE_ENTITY,
            },
            # Recurso não encontrado
            {
                "request": lambda c: c.get("/api/v1/nonexistent"),
                "expected_status": status.HTTP_404_NOT_FOUND,
            },
            # Método não permitido
            {
                "request": lambda c: c.post("/api/v1/operators"),
                "expected_status": status.HTTP_405_METHOD_NOT_ALLOWED,
            },
        ]

        # Executar cada cenário
        for scenario in error_scenarios:
            response = scenario["request"](client)

            # Verificar o status esperado
            assert (
                response.status_code == scenario["expected_status"]
            ), f"Status inesperado: {response.status_code} vs {scenario['expected_status']}"

            # Verificar a estrutura comum de erro
            error_response = response.json()
            assert "type" in error_response
            assert "title" in error_response
            assert "detail" in error_response
            assert "status" in error_response
            assert error_response["status"] == response.status_code

    def test_api_documentation_availability(self, client):
        """Teste para verificar a disponibilidade da documentação da API"""
        # Verificar Swagger UI
        response = client.get("/docs")
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]

        # Verificar ReDoc
        response = client.get("/redoc")
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]

        # Verificar OpenAPI JSON
        response = client.get("/openapi.json")
        assert response.status_code == status.HTTP_200_OK
        assert "application/json" in response.headers["content-type"]

        # Verificar se o esquema OpenAPI contém os endpoints esperados
        schema = response.json()
        assert "/api/v1/operators" in schema["paths"]

        # Verificar documentação do endpoint principal
        operator_endpoint = schema["paths"]["/api/v1/operators"]
        assert "get" in operator_endpoint
        assert "summary" in operator_endpoint["get"]
        assert "description" in operator_endpoint["get"]
        assert "parameters" in operator_endpoint["get"]
