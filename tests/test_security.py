import pytest
import re
from fastapi.testclient import TestClient
from unittest.mock import patch
from presentation.main import create_application
from presentation.model.pageable_response import PageableResponse

@pytest.fixture
def test_client():
    app = create_application()
    return TestClient(app)

@pytest.fixture
def mock_response():
    # Dados mockados para simular resultados do banco de dados
    mock_data = [
        {
            "id": 1,
            "operator_registry": "123456",
            "cnpj": "12345678901234",
            "corporate_name": "Empresa Teste 1",
            "trade_name": "Teste 1",
            "modality": "Cooperativa Médica",
            "street": "Rua Teste",
            "city": "São Paulo",
            "state": "SP",
            "email": "teste@teste.com"
        }
    ]
    
    return PageableResponse(
        data=mock_data,
        page=1,
        page_size=10,
        total_pages=1,
        total_items=1,
        query="",
        order_by="corporate_name",
        order_direction="asc"
    )

@pytest.mark.asyncio
@patch('application.services.operator_service.OperatorSearchService.find_all_cached')
async def test_sql_injection_protection(mock_find_all_cached, test_client, mock_response):
    # Configura o mock para retornar dados simulados
    mock_find_all_cached.return_value = mock_response
    
    # Lista de possíveis tentativas de injeção SQL
    sql_injection_attempts = [
        "' OR '1'='1",
        "'; DROP TABLE cadop.cadastro_operadoras; --",
        "' UNION SELECT * FROM users; --",
        "' OR '1'='1' --",
        "1; SELECT * FROM information_schema.tables",
        "corporate_name = 'hack' OR 1=1; --"
    ]
    
    # Testa cada tentativa de injeção SQL
    for injection in sql_injection_attempts:
        response = test_client.get(f"/api/v1/operators?query={injection}")
        
        # Verifica se a resposta é bem-sucedida (não resultou em erro de servidor)
        assert response.status_code != 500, f"Erro de servidor para injeção SQL: {injection}"
        
        # Se a resposta é 400, verifica se é devido à validação
        if response.status_code == 400:
            error = response.json()
            assert "detail" in error, "Resposta de erro não contém detalhes"
        
        # Se a resposta é 200, verifica se não retornou todos os operadores (o que indicaria sucesso da injeção)
        if response.status_code == 200:
            data = response.json()
            assert len(data["data"]) <= 1, f"Injeção SQL pode ter sido bem-sucedida: {injection}"

@pytest.mark.asyncio
@patch('application.services.operator_service.OperatorSearchService.find_all_cached')
async def test_invalid_parameter_handling(mock_find_all_cached, test_client):
    # Testa a manipulação de parâmetros inválidos
    invalid_params = [
        {"page": 0},  # Página inválida (menor que 1)
        {"page": "abc"},  # Página não numérica
        {"page_size": 0},  # Tamanho de página inválido (menor que 1)
        {"page_size": "abc"},  # Tamanho de página não numérico
        {"page_size": 1000},  # Tamanho de página muito grande
        {"order_direction": "invalid"},  # Direção de ordenação inválida
        {"query": "a"}  # Consulta muito curta (menos de 3 caracteres, conforme validação)
    ]
    
    # Testa cada parâmetro inválido
    for params in invalid_params:
        # Constrói a string de consulta
        query_params = "&".join([f"{k}={v}" for k, v in params.items()])
        response = test_client.get(f"/api/v1/operators?{query_params}")
        
        # Verifica se a resposta é 400 (Bad Request) para parâmetros inválidos
        assert response.status_code == 400, f"Parâmetro inválido não rejeitado: {params}"
        
        # Verifica se a resposta contém detalhes sobre o erro
        error = response.json()
        assert "detail" in error, "Resposta de erro não contém detalhes"

@pytest.mark.asyncio
@patch('application.services.operator_service.OperatorSearchService.find_all_cached')
async def test_xss_protection(mock_find_all_cached, test_client, mock_response):
    # Configura o mock para retornar dados simulados
    mock_find_all_cached.return_value = mock_response
    
    # Lista de possíveis tentativas de XSS
    xss_attempts = [
        "<script>alert('XSS')</script>",
        "<img src='x' onerror='alert(\"XSS\")'>",
        "<a href='javascript:alert(\"XSS\")'>link</a>",
        "' onclick='alert(\"XSS\")' '",
        "<svg/onload=alert('XSS')>"
    ]
    
    # Testa cada tentativa de XSS
    for xss in xss_attempts:
        response = test_client.get(f"/api/v1/operators?query={xss}")
        
        # Verifica se a resposta é bem-sucedida (não resultou em erro de servidor)
        assert response.status_code != 500, f"Erro de servidor para tentativa de XSS: {xss}"
        
        # Se a resposta é 200, verifica se o conteúdo XSS foi escapado (não está presente na resposta como está)
        if response.status_code == 200:
            response_text = response.text
            # Verifica se o script não foi renderizado como HTML válido
            assert xss not in response_text, f"Possível vulnerabilidade XSS detectada: {xss}"
            # Ou verifica se os caracteres especiais foram escapados
            assert "&lt;script&gt;" not in response_text or "&quot;" not in response_text, "Verificação de escape de caracteres falhou"

@pytest.mark.asyncio
@patch('application.services.operator_service.OperatorSearchService.find_all_cached')
async def test_path_traversal_protection(mock_find_all_cached, test_client):
    # Lista de possíveis tentativas de path traversal
    path_traversal_attempts = [
        "../../../etc/passwd",
        "/etc/passwd",
        "..\\..\\..\\Windows\\system.ini",
        "C:\\Windows\\system.ini",
        "file:///etc/passwd"
    ]
    
    # Testa cada tentativa de path traversal
    for path in path_traversal_attempts:
        response = test_client.get(f"/api/v1/operators?query={path}")
        
        # Verifica se a resposta não é um erro de servidor
        assert response.status_code != 500, f"Erro de servidor para tentativa de path traversal: {path}"
        
        # Verifica o conteúdo da resposta para garantir que não contém dados sensíveis
        response_text = response.text
        # Padrões que poderiam indicar acesso a arquivos do sistema
        sensitive_patterns = [
            "root:",  # Conteúdo típico de /etc/passwd
            "[System]",  # Conteúdo típico de system.ini
            "\\Windows\\",  # Caminhos do Windows
            "/etc/"  # Caminhos do Linux
        ]
        
        for pattern in sensitive_patterns:
            assert pattern not in response_text, f"Possível vulnerabilidade de path traversal detectada: {path}" 