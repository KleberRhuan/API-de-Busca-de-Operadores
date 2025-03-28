import pytest
from unittest.mock import patch
from fastapi import status

class TestOperatorsIntegration:
    """Testes de integração para o fluxo completo de busca de operadoras"""
    
    def test_operator_service_integration(self, client, mock_operator_service, paginated_operators_response):
        """Teste de integração do serviço de operadoras com o endpoint da API"""
        # Configurar o mock para retornar dados de exemplo
        mock_operator_service.find_all_cached.return_value = paginated_operators_response
        
        # Fazer a requisição para o endpoint
        response = client.get("/api/v1/operators?query=teste&page=1&page_size=10")
        
        # Verificar se a resposta tem o status correto
        assert response.status_code == status.HTTP_200_OK
        
        # Verificar se o serviço foi chamado com os parâmetros corretos
        mock_operator_service.find_all_cached.assert_called_once()
        
        # Extrair o argumento (request params) passado para o método find_all_cached
        args = mock_operator_service.find_all_cached.call_args[0]
        assert len(args) == 1
        params = args[0]
        
        # Verificar se os parâmetros estão corretos
        assert params.query == "teste"
        assert params.page == 1
        assert params.page_size == 10
        
    def test_database_redis_integration(self, client):
        """Teste de integração do Redis com o cache do sistema"""
        with patch("src.infra.database.cache.get") as mock_cache_get, \
             patch("src.infra.database.cache.set") as mock_cache_set, \
             patch("src.application.service.operator_service.OperatorService.find_all") as mock_find_all:
            
            # Configurar os mocks
            mock_cache_get.return_value = None  # Simular cache miss
            mock_find_all.return_value = {
                "content": [],
                "page": 1,
                "page_size": 10,
                "total_elements": 0,
                "total_pages": 0
            }
            
            # Fazer a requisição para o endpoint
            response = client.get("/api/v1/operators?query=teste")
            
            # Verificar se a resposta tem o status correto
            assert response.status_code == status.HTTP_200_OK
            
            # Verificar se o cache foi consultado
            mock_cache_get.assert_called_once()
            
            # Verificar se o método find_all foi chamado (devido ao cache miss)
            mock_find_all.assert_called_once()
            
            # Verificar se o resultado foi armazenado no cache
            mock_cache_set.assert_called_once()

class TestMiddlewareIntegration:
    """Testes de integração para os middlewares da aplicação"""
    
    def test_cors_headers(self, client):
        """Teste para verificar se os cabeçalhos CORS estão sendo aplicados corretamente"""
        # Fazer a requisição com cabeçalho Origin definido
        response = client.get("/api/v1/operators?query=teste", headers={"Origin": "localhost"})
        
        # Verificar se a resposta tem os cabeçalhos CORS esperados
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "localhost"
        
    def test_rate_limit_headers(self, client, mock_operator_service, paginated_operators_response):
        """Teste para verificar se os cabeçalhos de rate limit estão sendo aplicados corretamente"""
        # Configurar o mock para retornar dados de exemplo
        mock_operator_service.find_all_cached.return_value = paginated_operators_response
        
        # Fazer a requisição para o endpoint
        response = client.get("/api/v1/operators?query=teste")
        
        # Verificar se a resposta tem os cabeçalhos de rate limit
        assert "x-ratelimit-limit" in response.headers
        assert "x-ratelimit-remaining" in response.headers
        assert "x-ratelimit-reset" in response.headers
        
        # Verificar se os valores são números positivos
        assert int(response.headers["x-ratelimit-limit"]) > 0
        assert int(response.headers["x-ratelimit-remaining"]) >= 0
        assert int(response.headers["x-ratelimit-reset"]) >= 0 