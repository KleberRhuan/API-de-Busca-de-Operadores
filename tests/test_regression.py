import pytest
from fastapi import status
import json

class TestRegressionCases:
    """Testes de regressão para garantir que problemas corrigidos não voltem a ocorrer"""
    
    def test_short_query_validation(self, client):
        """Teste para garantir que a validação de consultas curtas continue funcionando"""
        # Verificar se queries curtas são rejeitadas corretamente
        response = client.get("/api/v1/operators?query=ab")
        
        # Verificar se a resposta tem o status correto
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Verificar a mensagem de erro
        data = response.json()
        assert "violations" in data
        assert any("query" in violation["name"] for violation in data["violations"])
        
        # Verificar se a mensagem contém a indicação do tamanho mínimo
        query_violation = next(v for v in data["violations"] if "query" in v["name"])
        assert any(word in query_violation["message"].lower() for word in ["mínimo", "minimum", "3"])
    
    def test_rate_limit_headers_present(self, client):
        """Teste para garantir que os cabeçalhos de rate limit continuem sendo retornados"""
        response = client.get("/api/v1/operators?query=teste")
        
        # Verificar se a resposta tem os cabeçalhos de rate limit
        assert "x-ratelimit-limit" in response.headers
        assert "x-ratelimit-remaining" in response.headers
        assert "x-ratelimit-reset" in response.headers
    
    def test_cors_headers_consistency(self, client):
        """Teste para garantir que os cabeçalhos CORS continuem consistentes"""
        # Verificar se os cabeçalhos CORS são retornados para origem permitida
        response = client.get("/api/v1/operators?query=teste", headers={"Origin": "localhost"})
        
        # Verificar cabeçalhos CORS
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-credentials" in response.headers
        assert "access-control-expose-headers" in response.headers
        
        # Verificar valores específicos
        assert response.headers["access-control-allow-origin"] == "localhost"
        assert response.headers["access-control-allow-credentials"] == "true"
        
        # Verificar headers expostos
        exposed_headers = response.headers["access-control-expose-headers"]
        for header in ["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset", "Retry-After"]:
            assert header in exposed_headers
    
    def test_pagination_parameters_handling(self, client, mock_operator_service):
        """Teste para garantir que os parâmetros de paginação continuem funcionando corretamente"""
        # Configurar o mock para retornar dados paginados
        mock_response = {
            "content": [],
            "page": 2,
            "page_size": 5,
            "total_elements": 0,
            "total_pages": 0
        }
        mock_operator_service.find_all_cached.return_value = mock_response
        
        # Testar com parâmetros de paginação personalizados
        response = client.get("/api/v1/operators?query=teste&page=2&page_size=5")
        
        # Verificar se a resposta tem o status correto
        assert response.status_code == status.HTTP_200_OK
        
        # Verificar se os parâmetros de paginação foram respeitados
        data = response.json()
        assert data["page"] == 2
        assert data["page_size"] == 5
        
        # Verificar se o serviço foi chamado com os parâmetros corretos
        args = mock_operator_service.find_all_cached.call_args[0][0]
        assert args.page == 2
        assert args.page_size == 5
    
    def test_error_response_structure(self, client):
        """Teste para garantir que a estrutura de resposta de erro continue consistente"""
        # Testar um endpoint inexistente
        response = client.get("/api/v1/nonexistent")
        
        # Verificar se a resposta tem o status correto
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Verificar a estrutura da resposta de erro
        data = response.json()
        required_fields = ["type", "title", "status", "detail", "userMessage"]
        for field in required_fields:
            assert field in data, f"Campo '{field}' ausente na resposta de erro"
        
        # Verificar valores específicos
        assert data["status"] == 404
        assert data["type"] == "https://httpstatuses.io/404"
    
    def test_query_cache_key_generation(self, client):
        """Teste para garantir que consultas idênticas usem o mesmo cache (regressão de cache)"""
        with pytest.mock.patch("src.infra.database.cache.get") as mock_cache_get, \
             pytest.mock.patch("src.infra.database.cache.set") as mock_cache_set, \
             pytest.mock.patch("src.application.service.operator_service.OperatorService.find_all") as mock_find_all:
            
            # Configurar mocks
            mock_cache_get.return_value = None  # Simular cache miss
            mock_find_all.return_value = {
                "content": [],
                "page": 1,
                "page_size": 10,
                "total_elements": 0,
                "total_pages": 0
            }
            
            # Fazer primeira requisição
            client.get("/api/v1/operators?query=teste&page=1&page_size=10")
            
            # Capturar a chave de cache usada
            cache_key_1 = mock_cache_set.call_args[0][0]
            
            # Resetar mocks
            mock_cache_get.reset_mock()
            mock_cache_set.reset_mock()
            mock_find_all.reset_mock()
            
            # Fazer segunda requisição idêntica mas com parâmetros em ordem diferente
            client.get("/api/v1/operators?page=1&query=teste&page_size=10")
            
            # Verificar se a chave de cache é a mesma
            cache_key_2 = mock_cache_get.call_args[0][0]
            
            # As chaves devem ser idênticas para consultas equivalentes
            assert cache_key_1 == cache_key_2, "Chaves de cache diferentes para consultas equivalentes" 