import pytest
import time
from unittest.mock import patch
import statistics

class TestApiPerformance:
    """Testes de performance para API"""
    
    @pytest.mark.performance
    def test_operators_endpoint_response_time(self, client, mock_operator_service, paginated_operators_response):
        """Teste para medir o tempo de resposta do endpoint de operadoras"""
        # Configurar o mock para retornar dados de exemplo
        mock_operator_service.find_all_cached.return_value = paginated_operators_response
        
        # Número de requisições para testar
        num_requests = 10
        response_times = []
        
        # Executar múltiplas requisições e medir o tempo
        for _ in range(num_requests):
            start_time = time.time()
            response = client.get("/api/v1/operators?query=teste")
            end_time = time.time()
            
            # Verificar se a resposta tem o status correto
            assert response.status_code == 200
            
            # Calcular o tempo de resposta em milissegundos
            response_time = (end_time - start_time) * 1000
            response_times.append(response_time)
        
        # Calcular estatísticas
        avg_response_time = statistics.mean(response_times)
        median_response_time = statistics.median(response_times)
        max_response_time = max(response_times)
        
        # Definir limites aceitáveis (ajustar conforme necessário)
        max_acceptable_avg = 200  # ms
        max_acceptable_max = 400  # ms
        
        # Imprimir resultados para análise
        print(f"\nTempo médio de resposta: {avg_response_time:.2f} ms")
        print(f"Tempo mediano de resposta: {median_response_time:.2f} ms")
        print(f"Tempo máximo de resposta: {max_response_time:.2f} ms")
        
        # Verificar se os tempos estão dentro dos limites aceitáveis
        assert avg_response_time < max_acceptable_avg, f"Tempo médio de resposta muito alto: {avg_response_time:.2f} ms"
        assert max_response_time < max_acceptable_max, f"Tempo máximo de resposta muito alto: {max_response_time:.2f} ms"

    @pytest.mark.performance
    def test_cache_performance(self, client):
        """Teste para medir o desempenho do cache"""
        with patch("src.infra.database.cache.get") as mock_cache_get, \
             patch("src.infra.database.cache.set") as mock_cache_set, \
             patch("src.application.service.operator_service.OperatorService.find_all") as mock_find_all:
            
            # Dados de exemplo para retorno
            sample_data = {
                "content": [{"id": 1, "nome_fantasia": "Operadora Teste"}],
                "page": 1,
                "page_size": 10,
                "total_elements": 1,
                "total_pages": 1
            }
            
            # Configurar primeiro acesso (cache miss)
            mock_cache_get.return_value = None
            mock_find_all.return_value = sample_data
            
            # Primeiro acesso (sem cache)
            start_time_no_cache = time.time()
            response_no_cache = client.get("/api/v1/operators?query=teste")
            end_time_no_cache = time.time()
            time_no_cache = (end_time_no_cache - start_time_no_cache) * 1000
            
            # Configurar segundo acesso (cache hit)
            mock_cache_get.return_value = sample_data
            
            # Segundo acesso (com cache)
            start_time_with_cache = time.time()
            response_with_cache = client.get("/api/v1/operators?query=teste")
            end_time_with_cache = time.time()
            time_with_cache = (end_time_with_cache - start_time_with_cache) * 1000
            
            # Imprimir resultados para análise
            print(f"\nTempo sem cache: {time_no_cache:.2f} ms")
            print(f"Tempo com cache: {time_with_cache:.2f} ms")
            print(f"Melhoria: {(1 - time_with_cache / time_no_cache) * 100:.2f}%")
            
            # O acesso com cache deve ser significativamente mais rápido
            assert time_with_cache < time_no_cache, "O acesso com cache não é mais rápido que sem cache"
            
            # Verificar se o método find_all foi chamado apenas uma vez (no primeiro acesso)
            mock_find_all.assert_called_once()
            
            # Verificar se o cache foi consultado duas vezes
            assert mock_cache_get.call_count == 2

    @pytest.mark.performance
    @pytest.mark.skip("Teste de carga deve ser executado separadamente em um ambiente controlado")
    def test_load_performance(self, client, mock_operator_service, paginated_operators_response):
        """Teste de carga para verificar o desempenho sob várias requisições concorrentes"""
        # Este teste deve ser executado em um ambiente controlado, não em CI/CD
        import threading
        
        # Configurar o mock para retornar dados de exemplo
        mock_operator_service.find_all_cached.return_value = paginated_operators_response
        
        # Número de requisições concorrentes
        num_concurrent = 50
        num_requests_per_thread = 10
        
        # Contador de requisições bem-sucedidas
        successful_requests = 0
        failed_requests = 0
        response_times = []
        
        # Lock para acessar contadores compartilhados
        lock = threading.Lock()
        
        def make_requests():
            nonlocal successful_requests, failed_requests
            local_success = 0
            local_failed = 0
            local_times = []
            
            for _ in range(num_requests_per_thread):
                try:
                    start_time = time.time()
                    response = client.get("/api/v1/operators?query=teste")
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        local_success += 1
                        local_times.append((end_time - start_time) * 1000)
                    else:
                        local_failed += 1
                except Exception:
                    local_failed += 1
            
            # Atualizar contadores globais
            with lock:
                successful_requests += local_success
                failed_requests += local_failed
                response_times.extend(local_times)
        
        # Criar e iniciar threads
        threads = []
        for _ in range(num_concurrent):
            thread = threading.Thread(target=make_requests)
            threads.append(thread)
            thread.start()
        
        # Aguardar todas as threads terminarem
        for thread in threads:
            thread.join()
        
        # Calcular estatísticas
        total_requests = successful_requests + failed_requests
        success_rate = (successful_requests / total_requests) * 100
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            median_response_time = statistics.median(response_times)
            p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)]
            max_response_time = max(response_times)
        else:
            avg_response_time = median_response_time = p95_response_time = max_response_time = 0
        
        # Imprimir resultados
        print(f"\nTotal de requisições: {total_requests}")
        print(f"Requisições bem-sucedidas: {successful_requests} ({success_rate:.2f}%)")
        print(f"Requisições falhas: {failed_requests}")
        print(f"Tempo médio de resposta: {avg_response_time:.2f} ms")
        print(f"Tempo mediano de resposta: {median_response_time:.2f} ms")
        print(f"Tempo de resposta P95: {p95_response_time:.2f} ms")
        print(f"Tempo máximo de resposta: {max_response_time:.2f} ms")
        
        # Verificar resultados
        assert success_rate > 95, f"Taxa de sucesso muito baixa: {success_rate:.2f}%"
        assert avg_response_time < 500, f"Tempo médio de resposta muito alto: {avg_response_time:.2f} ms"
        assert p95_response_time < 1000, f"Tempo P95 muito alto: {p95_response_time:.2f} ms" 