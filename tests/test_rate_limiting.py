import pytest
import time
from fastapi import status
from unittest.mock import patch
import threading

class TestRateLimiting:
    """Testes para verificar o funcionamento do rate limiting"""
    
    def test_rate_limit_exceeded(self, client, mock_operator_service, mock_memory_storage):
        """Teste para verificar se o rate limiting bloqueia requisições após exceder o limite"""
        # No ambiente de teste o limite está configurado como 10 requisições em 10 segundos
        
        # Configurar o storage de rate limiting
        with patch("src.infra.middleware.rate_limit_middleware.RateLimitMiddleware.__init__", return_value=None) as mock_init, \
             patch("src.infra.middleware.rate_limit_middleware.RateLimitMiddleware.dispatch") as mock_dispatch:
            
            # Fazer o mock retornar à implementação original
            mock_init.side_effect = lambda *args, **kwargs: None
            mock_dispatch.side_effect = lambda request, call_next: call_next(request)
            
            # Número de requisições a executar (superior ao limite configurado)
            num_requests = 15
            
            # Armazenar respostas
            responses = []
            
            # Executar as requisições
            for i in range(num_requests):
                # Adicionar um parâmetro único para evitar possível cache
                response = client.get(f"/api/v1/operators?query=teste&cache_buster={i}")
                responses.append(response)
            
            # Verificar os resultados
            num_success = sum(1 for r in responses if r.status_code == status.HTTP_200_OK)
            num_blocked = sum(1 for r in responses if r.status_code == status.HTTP_429_TOO_MANY_REQUESTS)
            
            # Deve haver exatamente 10 requisições bem-sucedidas e 5 bloqueadas
            assert num_success == 10, f"Número incorreto de requisições bem-sucedidas: {num_success}, esperado: 10"
            assert num_blocked == 5, f"Número incorreto de requisições bloqueadas: {num_blocked}, esperado: 5"
    
    def test_rate_limit_headers(self, client):
        """Teste para verificar os cabeçalhos de rate limit"""
        # Fazer a requisição
        response = client.get("/api/v1/operators?query=teste")
        
        # Verificar se a resposta tem os cabeçalhos de rate limit
        assert "x-ratelimit-limit" in response.headers, "Cabeçalho X-RateLimit-Limit ausente"
        assert "x-ratelimit-remaining" in response.headers, "Cabeçalho X-RateLimit-Remaining ausente"
        assert "x-ratelimit-reset" in response.headers, "Cabeçalho X-RateLimit-Reset ausente"
        
        # Verificar valores
        limit = int(response.headers["x-ratelimit-limit"])
        remaining = int(response.headers["x-ratelimit-remaining"])
        reset = int(response.headers["x-ratelimit-reset"])
        
        # Ambiente de teste configura limite como 10
        assert limit == 10, f"Valor incorreto para X-RateLimit-Limit: {limit}, esperado: 10"
        assert remaining == 9, f"Valor incorreto para X-RateLimit-Remaining: {remaining}, esperado: 9"
        assert reset > 0, f"Valor incorreto para X-RateLimit-Reset: {reset}, deve ser positivo"
    
    def test_rate_limit_error_format(self, client):
        """Teste para verificar formato do erro de rate limit"""
        # Configurar um mock para forçar erro de rate limit
        with patch("src.infra.middleware.rate_limit_middleware.RateLimitMiddleware.dispatch") as mock_dispatch:
            from src.application.exception.rate_limit_exception import RateLimitExceededException
            
            # Forçar erro de rate limit
            mock_dispatch.side_effect = RateLimitExceededException(limit=10, window=10, reset_in=5)
            
            # Fazer a requisição
            response = client.get("/api/v1/operators?query=teste")
            
            # Verificar status
            assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS, "Status incorreto para erro de rate limit"
            
            # Verificar cabeçalhos
            assert "retry-after" in response.headers, "Cabeçalho Retry-After ausente"
            
            # Verificar corpo da resposta
            data = response.json()
            assert "type" in data, "Campo 'type' ausente na resposta de erro"
            assert "title" in data, "Campo 'title' ausente na resposta de erro"
            assert "detail" in data, "Campo 'detail' ausente na resposta de erro"
            assert "status" in data, "Campo 'status' ausente na resposta de erro"
            assert "userMessage" in data, "Campo 'userMessage' ausente na resposta de erro"
            
            # Verificar valores específicos
            assert data["type"] == "https://httpstatuses.io/429", "Tipo de erro incorreto"
            assert data["status"] == 429, "Status incorreto na resposta de erro"
            assert "limite" in data["detail"].lower(), "Detalhe não menciona o limite"
    
    def test_rate_limit_window_reset(self, client):
        """Teste para verificar se o rate limit é restaurado após o período de janela"""
        # Este teste é mais difícil em uma unidade de teste porque requer esperar o tempo da janela
        # Portanto, usamos mocks para simular o comportamento
        
        with patch("src.infra.middleware.rate_limit_middleware.MovingWindowRateLimiter.hit") as mock_hit:
            # Simular primeiro o limite sendo atingido
            mock_hit.side_effect = [True] * 10 + [False] * 5 + [True] * 10
            
            # Fase 1: Fazer 10 requisições bem-sucedidas
            for i in range(10):
                response = client.get(f"/api/v1/operators?query=teste&phase=1&i={i}")
                assert response.status_code == status.HTTP_200_OK, f"Requisição {i+1} falhou inesperadamente"
            
            # Fase 2: Fazer 5 requisições que serão bloqueadas
            for i in range(5):
                response = client.get(f"/api/v1/operators?query=teste&phase=2&i={i}")
                assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS, f"Requisição {i+1} não foi bloqueada como esperado"
            
            # Fase 3: Simular o tempo passando e a janela sendo restaurada
            # Em um teste real isso seria algo como `time.sleep(window_seconds)`
            # Aqui usamos o mock para simular que o limite foi reiniciado
            
            # Fazer mais 10 requisições que devem ser bem-sucedidas novamente
            for i in range(10):
                response = client.get(f"/api/v1/operators?query=teste&phase=3&i={i}")
                assert response.status_code == status.HTTP_200_OK, f"Requisição {i+1} falhou após reset da janela"
    
    @pytest.mark.skip("Teste de concorrência deve ser executado separadamente")
    def test_rate_limit_concurrent_requests(self, client):
        """Teste para verificar o comportamento do rate limiting em requisições concorrentes"""
        # Número de threads para simular requisições concorrentes
        num_threads = 20
        
        # Armazenar resultados
        results = []
        lock = threading.Lock()
        
        def make_request():
            response = client.get("/api/v1/operators?query=teste")
            with lock:
                results.append(response.status_code)
        
        # Criar e iniciar threads
        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Aguardar todas as threads terminarem
        for thread in threads:
            thread.join()
        
        # Contar resultados
        num_success = results.count(status.HTTP_200_OK)
        num_blocked = results.count(status.HTTP_429_TOO_MANY_REQUESTS)
        
        # Verificar se exatamente 10 requisições foram bem-sucedidas e o restante bloqueado
        assert num_success == 10, f"Número incorreto de requisições bem-sucedidas: {num_success}, esperado: 10"
        assert num_blocked == 10, f"Número incorreto de requisições bloqueadas: {num_blocked}, esperado: 10" 