import pytest
from fastapi import status

class TestOperatorsEndpoint:
    """Testes funcionais para o endpoint de operadoras"""
    
    def test_search_operators_success(self, client, mock_operator_service, paginated_operators_response):
        """Teste para verificar se a busca de operadoras retorna com sucesso"""
        # Configurar o mock para retornar dados de exemplo
        mock_operator_service.find_all_cached.return_value = paginated_operators_response
        
        # Fazer a requisição para o endpoint - usando query com pelo menos 3 caracteres
        response = client.get("/api/v1/operators?query=operadora")
        
        # Verificar se a resposta tem o status correto
        assert response.status_code == status.HTTP_200_OK
        
        # Verificar se a resposta contém os dados esperados
        data = response.json()
        assert "data" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_items" in data
        assert "total_pages" in data
        assert len(data["data"]) == 2
        
    def test_search_operators_empty_results(self, client, mock_operator_service):
        """Teste para verificar se a busca de operadoras com resultados vazios é tratada corretamente"""
        # Configurar o mock para retornar dados vazios
        empty_response = {
            "data": [],
            "page": 1,
            "page_size": 10,
            "total_items": 0,
            "total_pages": 0,
            "query": "naoexiste",
            "order_by": None,
            "order_direction": "asc"
        }
        mock_operator_service.find_all_cached.return_value = empty_response
        
        # Fazer a requisição para o endpoint
        response = client.get("/api/v1/operators")
        
        # Verificar se a resposta tem o status correto
        assert response.status_code == status.HTTP_200_OK
        
        # Verificar se a resposta contém os dados vazios esperados
        data = response.json()
        assert "data" in data
        assert len(data["data"]) == 0
        assert data["total_items"] == 0
        
    def test_search_operators_invalid_query(self, client):
        """Teste para verificar se a validação de query muito curta funciona"""
        # Fazer a requisição para o endpoint com uma query muito curta
        response = client.get("/api/v1/operators?query=ab")
        
        # Verificar se a resposta tem o status de erro de validação
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Verificar se a mensagem de erro está correta
        data = response.json()
        assert "violations" in data
        assert any("query" in violation["name"] for violation in data["violations"])

class TestApplicationHealth:
    """Testes para verificar a saúde da aplicação"""
    
    @pytest.mark.skip("Implementar endpoint de health check")
    def test_health_check(self, client):
        """Teste para verificar se o health check da aplicação está funcionando"""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "UP"

# Se o ambiente de teste estiver em modo de desenvolvimento, testar o endpoint de cache
class TestCacheEndpoint:
    """Testes para o endpoint de cache (apenas em ambiente de desenvolvimento)"""
    
    def test_cache_endpoint_in_dev_mode(self, client, mock_redis):
        """Teste para verificar se o endpoint de cache está funcionando corretamente"""
        # Configurar o mock do Redis para simular uma operação de cache bem-sucedida
        import os
        if os.getenv("ENV") != "dev":
            pytest.skip("Teste só é executado em ambiente de desenvolvimento")
            
        # Fazer a requisição para o endpoint de teste de cache
        response = client.get("/api/v1/cache-test")
        
        # Verificar a resposta
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "cached_value" in data 