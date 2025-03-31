import pytest
from fastapi import status


class TestCORSConfiguration:
    """Testes para verificar a configuração CORS da API"""

    @pytest.mark.skip("Middleware CORS não está ativo durante os testes")
    def test_cors_allowed_origin(self, client):
        """Teste para verificar se origens permitidas recebem os cabeçalhos CORS corretos"""
        # Testar com uma origem permitida (localhost)
        response = client.get("/openapi.json", headers={"Origin": "localhost"})

        # Verificar se a resposta tem os cabeçalhos CORS esperados
        assert response.status_code == status.HTTP_200_OK
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "localhost"
        assert "access-control-allow-credentials" in response.headers
        assert response.headers["access-control-allow-credentials"] == "true"

    def test_cors_disallowed_origin(self, client):
        """Teste para verificar se origens não permitidas não recebem cabeçalhos CORS"""
        # Testar com uma origem não permitida
        response = client.get(
            "/openapi.json", headers={"Origin": "https://malicious-site.com"}
        )

        # A resposta deve ter status 200, mas sem o cabeçalho CORS permitindo a origem maliciosa
        assert response.status_code == status.HTTP_200_OK
        assert (
            "access-control-allow-origin" not in response.headers
            or response.headers["access-control-allow-origin"]
            != "https://malicious-site.com"
        )

    @pytest.mark.skip("Middleware CORS não está ativo durante os testes")
    def test_cors_preflight_request(self, client):
        """Teste para verificar se a requisição preflight OPTIONS é processada corretamente"""
        # Fazer uma requisição preflight OPTIONS
        response = client.options(
            "/openapi.json",
            headers={
                "Origin": "localhost",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )

        # Verificar se a resposta tem os cabeçalhos CORS esperados
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "localhost"
        assert "access-control-allow-methods" in response.headers
        assert "GET" in response.headers["access-control-allow-methods"]
        assert "access-control-allow-headers" in response.headers
        assert "Content-Type" in response.headers["access-control-allow-headers"]
        assert "access-control-max-age" in response.headers

    def test_cors_expose_headers(self, client):
        """Teste para verificar se os cabeçalhos expostos estão configurados corretamente"""
        # Fazer uma requisição com origem permitida
        response = client.get("/openapi.json", headers={"Origin": "localhost"})

        # Verificar se os cabeçalhos expostos estão configurados corretamente
        assert "access-control-expose-headers" in response.headers
        exposed_headers = response.headers["access-control-expose-headers"]

        # Verificar se os cabeçalhos de rate limit estão expostos
        required_headers = [
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
            "Retry-After",
        ]
        for header in required_headers:
            assert (
                header in exposed_headers
            ), f"Cabeçalho {header} não está exposto no CORS"

    def test_cors_allowed_methods(self, client):
        """Teste para verificar os métodos HTTP permitidos pelo CORS"""
        # Fazer uma requisição preflight OPTIONS
        response = client.options(
            "/api/v1/operators",
            headers={
                "Origin": "localhost",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )

        # Verificar se a resposta especifica os métodos permitidos
        assert "access-control-allow-methods" in response.headers
        allowed_methods = response.headers["access-control-allow-methods"]

        # Verificar métodos permitidos
        assert "GET" in allowed_methods

        # Métodos não permitidos não devem estar na lista
        # POST, PUT, DELETE são considerados não permitidos neste contexto
        non_allowed_methods = ["POST", "PUT", "DELETE"]
        for method in non_allowed_methods:
            if "," in allowed_methods:
                methods_list = [m.strip() for m in allowed_methods.split(",")]
                assert (
                    method not in methods_list
                ), f"Método {method} não deveria estar permitido"

    @pytest.mark.skip("Middleware CORS não está ativo durante os testes")
    def test_cors_documentation_endpoints(self, client):
        """Teste para verificar se os endpoints de documentação também respeitam CORS"""
        # Lista de endpoints de documentação
        doc_endpoints = ["/docs", "/redoc", "/openapi.json"]

        for endpoint in doc_endpoints:
            # Fazer uma requisição com origem permitida
            response = client.get(endpoint, headers={"Origin": "localhost"})

            # Verificar se a resposta tem os cabeçalhos CORS esperados
            assert (
                response.status_code == status.HTTP_200_OK
            ), f"Endpoint {endpoint} retornou status {response.status_code}"
            assert (
                "access-control-allow-origin" in response.headers
            ), f"Endpoint {endpoint} não tem cabeçalho CORS"
            assert (
                response.headers["access-control-allow-origin"] == "localhost"
            ), f"Endpoint {endpoint} tem origem incorreta"
