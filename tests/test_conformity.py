import pytest
from fastapi import status
import re
import json

class TestAPIConformity:
    """Testes para verificar a conformidade da API com padrões e melhores práticas"""
    
    def test_rest_api_conventions(self, client):
        """Teste para verificar se a API segue as convenções REST"""
        # Verificar nomes de endpoints (substantivos no plural)
        response = client.get("/openapi.json")
        schema = response.json()
        
        for path in schema["paths"].keys():
            if path not in ["/docs", "/redoc", "/openapi.json"]:
                # Verificar se o path possui segmentos, excluindo parâmetros
                segments = [s for s in path.split("/") if s and "{" not in s]
                
                # Verificar se o último segmento é um substantivo no plural
                if segments:
                    last_segment = segments[-1]
                    assert last_segment.endswith("s") or last_segment.endswith("es"), \
                        f"Endpoint '{path}' não segue a convenção de substantivos no plural"
    
    def test_http_status_codes_usage(self, client, mock_operator_service):
        """Teste para verificar o uso correto de códigos de status HTTP"""
        # Verificar códigos de status para diferentes situações
        
        # 1. Sucesso (200)
        mock_operator_service.find_all_cached.return_value = {
            "content": [],
            "page": 1,
            "page_size": 10,
            "total_elements": 0,
            "total_pages": 0
        }
        response = client.get("/api/v1/operators?query=teste")
        assert response.status_code == status.HTTP_200_OK
        
        # 2. Não encontrado (404)
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # 3. Erro de validação (422)
        response = client.get("/api/v1/operators?query=ab")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # 4. Método não permitido (405)
        response = client.post("/api/v1/operators")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    
    def test_response_content_type(self, client):
        """Teste para verificar se os tipos de conteúdo das respostas estão corretos"""
        # API deve retornar JSON
        response = client.get("/api/v1/operators?query=teste")
        assert "application/json" in response.headers["content-type"]
        
        # Documentação Swagger
        response = client.get("/docs")
        assert "text/html" in response.headers["content-type"]
        
        # Documentação ReDoc
        response = client.get("/redoc")
        assert "text/html" in response.headers["content-type"]
        
        # Esquema OpenAPI
        response = client.get("/openapi.json")
        assert "application/json" in response.headers["content-type"]
    
    def test_openapi_specification_conformity(self, client):
        """Teste para verificar conformidade com a especificação OpenAPI"""
        response = client.get("/openapi.json")
        schema = response.json()
        
        # Verificar elementos obrigatórios da especificação OpenAPI 3.0
        assert "openapi" in schema
        assert schema["openapi"].startswith("3.0")  # Versão 3.0.x
        assert "info" in schema
        assert "title" in schema["info"]
        assert "version" in schema["info"]
        assert "paths" in schema
        
        # Verificar definição de componentes/esquemas
        assert "components" in schema
        assert "schemas" in schema["components"]
        
        # Verificar esquemas de modelos
        required_schemas = ["OperatorModel", "PageableResponse", "ApiError", "Violation"]
        for schema_name in required_schemas:
            assert schema_name in schema["components"]["schemas"], f"Esquema '{schema_name}' não encontrado"
        
        # Verificar se todos os endpoints têm documentação
        for path, methods in schema["paths"].items():
            if path not in ["/docs", "/redoc", "/openapi.json"]:
                for method, spec in methods.items():
                    assert "summary" in spec, f"Resumo não definido para {method.upper()} {path}"
                    assert "description" in spec, f"Descrição não definida para {method.upper()} {path}"
                    if "parameters" in spec:
                        for param in spec["parameters"]:
                            assert "description" in param, f"Descrição não definida para parâmetro '{param.get('name', 'desconhecido')}' em {method.upper()} {path}"
    
    def test_semantic_versioning(self, client):
        """Teste para verificar se a API segue versionamento semântico"""
        response = client.get("/openapi.json")
        schema = response.json()
        
        # Verificar a versão da API
        api_version = schema["info"]["version"]
        
        # Verificar formato de versionamento semântico (MAJOR.MINOR.PATCH)
        semver_pattern = r'^\d+\.\d+\.\d+$'
        assert re.match(semver_pattern, api_version), \
            f"Versão da API '{api_version}' não segue o padrão de versionamento semântico"
    
    def test_consistent_naming_convention(self, client):
        """Teste para verificar se os nomes de campos seguem uma convenção consistente"""
        response = client.get("/openapi.json")
        schema = response.json()
        
        # Verificar convenção de nomes nos esquemas
        for schema_name, schema_def in schema["components"]["schemas"].items():
            if "properties" in schema_def:
                # Verificar se todos os campos seguem o mesmo padrão (camelCase ou snake_case)
                properties = schema_def["properties"].keys()
                
                if properties:
                    # Verificar se há algum campo em camelCase
                    has_camel_case = any(re.search(r'[a-z][A-Z]', prop) for prop in properties)
                    
                    # Verificar se há algum campo em snake_case
                    has_snake_case = any(re.search(r'_', prop) for prop in properties)
                    
                    # Não deve haver mistura de convenções
                    assert not (has_camel_case and has_snake_case), \
                        f"Esquema '{schema_name}' mistura convenções de nomenclatura (camelCase e snake_case)" 