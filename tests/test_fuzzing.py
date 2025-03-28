import pytest
import random
import string
import requests
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

def generate_random_string(length=10):
    """Gera uma string aleatória de tamanho especificado"""
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))

def generate_random_number(min_val=1, max_val=1000):
    """Gera um número aleatório entre min_val e max_val"""
    return random.randint(min_val, max_val)

def generate_random_unicode():
    """Gera uma string com caracteres Unicode aleatórios"""
    # Intervalos de caracteres Unicode interessantes para teste
    unicode_ranges = [
        (0x0021, 0x007E),  # ASCII
        (0x00A1, 0x00FF),  # Latin-1 Supplement
        (0x0100, 0x017F),  # Latin Extended-A
        (0x0180, 0x024F),  # Latin Extended-B
        (0x0370, 0x03FF),  # Greek and Coptic
        (0x0400, 0x04FF),  # Cyrillic
        (0x0530, 0x058F),  # Armenian
        (0x0590, 0x05FF),  # Hebrew
        (0x0600, 0x06FF),  # Arabic
        (0x0900, 0x097F),  # Devanagari
        (0x4E00, 0x9FFF),  # CJK Unified Ideographs (subset)
        (0xAC00, 0xD7AF),  # Hangul Syllables (subset)
    ]
    
    result = ""
    for _ in range(random.randint(1, 10)):
        start, end = random.choice(unicode_ranges)
        char_code = random.randint(start, end)
        result += chr(char_code)
    
    return result

@pytest.mark.asyncio
@patch('application.services.operator_service.OperatorSearchService.find_all_cached')
async def test_random_query_parameter_fuzzing(mock_find_all_cached, test_client, mock_response):
    """Testa o endpoint com parâmetros de consulta aleatórios"""
    # Configura o mock para retornar dados simulados
    mock_find_all_cached.return_value = mock_response
    
    # Número de testes aleatórios a serem executados
    num_tests = 50
    
    for _ in range(num_tests):
        # Gera um valor aleatório para o parâmetro "query"
        random_type = random.choice(["string", "long_string", "unicode", "special_chars"])
        
        if random_type == "string":
            query_value = generate_random_string(random.randint(3, 15))
        elif random_type == "long_string":
            query_value = generate_random_string(random.randint(100, 500))
        elif random_type == "unicode":
            query_value = generate_random_unicode()
        else:  # special_chars
            query_value = ''.join(random.choice(string.punctuation) for _ in range(random.randint(3, 15)))
        
        # Faz a requisição para o endpoint
        try:
            response = test_client.get(f"/api/v1/operators?query={query_value}")
            
            # Verifica se a resposta é bem-sucedida (200) ou uma resposta de erro válida (400)
            assert response.status_code in [200, 400], f"Código de status inválido {response.status_code} para query='{query_value}'"
            
            # Se a resposta for um erro 400, verifica se tem uma mensagem de erro válida
            if response.status_code == 400:
                error = response.json()
                assert "detail" in error, f"Resposta de erro sem detalhe para query='{query_value}'"
                
        except requests.exceptions.RequestException as e:
            assert False, f"Exceção ao fazer requisição com query='{query_value}': {str(e)}"
        except Exception as e:
            assert False, f"Erro inesperado ao processar query='{query_value}': {str(e)}"

@pytest.mark.asyncio
@patch('application.services.operator_service.OperatorSearchService.find_all_cached')
async def test_random_page_parameter_fuzzing(mock_find_all_cached, test_client, mock_response):
    """Testa o endpoint com parâmetros de página aleatórios"""
    # Configura o mock para retornar dados simulados
    mock_find_all_cached.return_value = mock_response
    
    # Número de testes aleatórios a serem executados
    num_tests = 50
    
    for _ in range(num_tests):
        # Gera valores aleatórios para os parâmetros de paginação
        random_type = random.choice(["valid", "invalid", "string", "special"])
        
        if random_type == "valid":
            page = random.randint(1, 1000)
            page_size = random.randint(1, 100)
        elif random_type == "invalid":
            page = random.randint(-1000, 0)
            page_size = random.randint(-1000, 0)
        elif random_type == "string":
            page = generate_random_string()
            page_size = generate_random_string()
        else:  # special
            page = random.choice(["null", "undefined", "NaN", "Infinity", "-Infinity"])
            page_size = random.choice(["null", "undefined", "NaN", "Infinity", "-Infinity"])
        
        # Faz a requisição para o endpoint
        try:
            response = test_client.get(f"/api/v1/operators?page={page}&page_size={page_size}")
            
            # Verifica se a resposta é bem-sucedida (200) ou uma resposta de erro válida (400)
            assert response.status_code in [200, 400, 422], f"Código de status inválido {response.status_code} para page={page}, page_size={page_size}"
            
        except requests.exceptions.RequestException as e:
            assert False, f"Exceção ao fazer requisição com page={page}, page_size={page_size}: {str(e)}"
        except Exception as e:
            assert False, f"Erro inesperado ao processar page={page}, page_size={page_size}: {str(e)}"

@pytest.mark.asyncio
@patch('application.services.operator_service.OperatorSearchService.find_all_cached')
async def test_random_ordering_parameter_fuzzing(mock_find_all_cached, test_client, mock_response):
    """Testa o endpoint com parâmetros de ordenação aleatórios"""
    # Configura o mock para retornar dados simulados
    mock_find_all_cached.return_value = mock_response
    
    # Número de testes aleatórios a serem executados
    num_tests = 50
    
    for _ in range(num_tests):
        # Gera valores aleatórios para os parâmetros de ordenação
        random_type = random.choice(["valid", "invalid", "special"])
        
        if random_type == "valid":
            order_by = random.choice(["id", "corporate_name", "trade_name", "cnpj", "operator_registry"])
            order_direction = random.choice(["asc", "desc"])
        elif random_type == "invalid":
            order_by = generate_random_string()
            order_direction = generate_random_string()
        else:  # special
            order_by = random.choice(["", "null", "undefined", "NaN", "Infinity"])
            order_direction = random.choice(["", "null", "undefined", "NaN", "ascending", "descending"])
        
        # Faz a requisição para o endpoint
        try:
            response = test_client.get(f"/api/v1/operators?order_by={order_by}&order_direction={order_direction}")
            
            # Verifica se a resposta é bem-sucedida (200) ou uma resposta de erro válida (400)
            assert response.status_code in [200, 400, 422], f"Código de status inválido {response.status_code} para order_by={order_by}, order_direction={order_direction}"
            
        except requests.exceptions.RequestException as e:
            assert False, f"Exceção ao fazer requisição com order_by={order_by}, order_direction={order_direction}: {str(e)}"
        except Exception as e:
            assert False, f"Erro inesperado ao processar order_by={order_by}, order_direction={order_direction}: {str(e)}"

@pytest.mark.asyncio
@patch('application.services.operator_service.OperatorSearchService.find_all_cached')
async def test_multiple_random_parameters_fuzzing(mock_find_all_cached, test_client, mock_response):
    """Testa o endpoint com múltiplos parâmetros aleatórios ao mesmo tempo"""
    # Configura o mock para retornar dados simulados
    mock_find_all_cached.return_value = mock_response
    
    # Número de testes aleatórios a serem executados
    num_tests = 50
    
    for _ in range(num_tests):
        # Gera uma quantidade aleatória de parâmetros
        num_params = random.randint(1, 10)
        
        params = {}
        
        # Lista de possíveis parâmetros
        possible_params = [
            "query", "page", "page_size", "order_by", "order_direction",
            "filter", "sort", "limit", "offset", "fields", "include", "exclude",
            "start_date", "end_date", "status", "type", "format"
        ]
        
        # Adiciona parâmetros aleatórios
        for _ in range(num_params):
            param_name = random.choice(possible_params)
            
            # Gera um valor aleatório para o parâmetro
            value_type = random.choice(["string", "number", "special"])
            
            if value_type == "string":
                param_value = generate_random_string()
            elif value_type == "number":
                param_value = generate_random_number()
            else:  # special
                param_value = random.choice(["", "null", "undefined", "NaN", "Infinity", "-Infinity"])
            
            params[param_name] = param_value
        
        # Constrói a string de consulta
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        
        # Faz a requisição para o endpoint
        try:
            response = test_client.get(f"/api/v1/operators?{query_string}")
            
            # Verifica se a resposta é um código de status válido
            assert response.status_code in [200, 400, 422], f"Código de status inválido {response.status_code} para params={params}"
            
        except requests.exceptions.RequestException as e:
            assert False, f"Exceção ao fazer requisição com params={params}: {str(e)}"
        except Exception as e:
            assert False, f"Erro inesperado ao processar params={params}: {str(e)}"

@pytest.mark.asyncio
@patch('application.services.operator_service.OperatorSearchService.find_all_cached')
async def test_fuzzing_request_methods(mock_find_all_cached, test_client, mock_response):
    """Testa diferentes métodos HTTP no endpoint de operadores"""
    # Configura o mock para retornar dados simulados
    mock_find_all_cached.return_value = mock_response
    
    # Lista de métodos HTTP a serem testados
    http_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]
    
    for method in http_methods:
        # Faz a requisição para o endpoint com diferentes métodos
        try:
            response = test_client.request(method, "/api/v1/operators")
            
            if method == "GET" or method == "HEAD" or method == "OPTIONS":
                # Para métodos suportados, verifica se a resposta é bem-sucedida
                assert response.status_code in [200, 204, 304], f"Código de status inválido {response.status_code} para método {method}"
            else:
                # Para métodos não suportados, verifica se a resposta é um erro 405 (Method Not Allowed)
                assert response.status_code == 405, f"Código de status inválido {response.status_code} para método {method}"
            
        except requests.exceptions.RequestException as e:
            assert False, f"Exceção ao fazer requisição com método {method}: {str(e)}"
        except Exception as e:
            assert False, f"Erro inesperado ao processar método {method}: {str(e)}"