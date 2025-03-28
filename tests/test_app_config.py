import pytest
import os
from unittest.mock import patch, MagicMock
from fastapi import FastAPI

class TestAppConfiguration:
    """Testes para verificar a configuração da aplicação"""
    
    def test_app_initialization(self, test_app):
        """Teste para verificar se a aplicação é inicializada corretamente"""
        # Verificar se a aplicação é uma instância de FastAPI
        assert isinstance(test_app, FastAPI)
        
        # Verificar se a aplicação tem título
        assert test_app.title, "Aplicação não tem título definido"
        
        # Verificar se a aplicação tem descrição
        assert test_app.description, "Aplicação não tem descrição definida"
        
        # Verificar se a aplicação tem versão
        assert test_app.version, "Aplicação não tem versão definida"
        
        # Verificar se a aplicação tem informações de contato
        assert test_app.contact, "Aplicação não tem informações de contato definidas"
    
    def test_env_loading(self):
        """Teste para verificar se as variáveis de ambiente são carregadas corretamente"""
        # Simular ambiente de desenvolvimento
        with patch.dict(os.environ, {"ENV": "dev"}):
            from src.infra.config.config import load_env
            
            # Simular o carregamento do .env
            with patch("dotenv.load_dotenv") as mock_load_dotenv:
                load_env()
                mock_load_dotenv.assert_called_once()
        
        # Simular ambiente de produção
        with patch.dict(os.environ, {"ENV": "prod"}):
            from src.infra.config.config import load_env
            
            # O .env não deve ser carregado em produção
            with patch("dotenv.load_dotenv") as mock_load_dotenv:
                load_env()
                mock_load_dotenv.assert_not_called()
    
    def test_rate_limit_configuration(self):
        """Teste para verificar se a configuração de rate limit é aplicada corretamente"""
        # Valores de configuração
        rate_limit = 100
        rate_window = 60
        
        # Simular ambiente com valores configurados
        with patch.dict(os.environ, {"RATE_LIMIT": str(rate_limit), "RATE_WINDOW": str(rate_window)}):
            # Criar um mock para a aplicação
            app_mock = MagicMock()
            
            # Importar função de configuração
            from src.infra.config.config import setup_application
            
            # Simular RateLimitMiddleware
            with patch("src.infra.middleware.rate_limit_middleware.RateLimitMiddleware") as mock_middleware:
                # Configurar a aplicação
                setup_application(app_mock)
                
                # Verificar se o middleware foi adicionado com os parâmetros corretos
                app_mock.add_middleware.assert_called()
                
                # Extrair os argumentos da chamada
                args, kwargs = app_mock.add_middleware.call_args
                
                # Verificar se o primeiro argumento é o middleware correto
                assert args[0] == mock_middleware
                
                # Verificar se os parâmetros estão corretos
                assert kwargs["limit"] == rate_limit
                assert kwargs["window"] == rate_window
    
    def test_cors_configuration(self):
        """Teste para verificar se a configuração CORS é aplicada corretamente"""
        # Criar um mock para a aplicação
        app_mock = MagicMock()
        
        # Importar função de configuração
        from src.infra.middleware.cors_middleware import setup_cors
        
        # Simular CORSMiddleware
        with patch("fastapi.middleware.cors.CORSMiddleware") as mock_middleware:
            # Configurar CORS
            setup_cors(app_mock)
            
            # Verificar se o middleware foi adicionado
            app_mock.add_middleware.assert_called_once()
            
            # Extrair os argumentos da chamada
            args, kwargs = app_mock.add_middleware.call_args
            
            # Verificar se o primeiro argumento é o middleware correto
            assert args[0] == mock_middleware
            
            # Verificar origens permitidas
            assert "allow_origins" in kwargs
            assert "localhost" in kwargs["allow_origins"]
            
            # Verificar métodos permitidos
            assert "allow_methods" in kwargs
            assert "GET" in kwargs["allow_methods"]
            
            # Verificar cabeçalhos permitidos
            assert "allow_headers" in kwargs
            assert "Content-Type" in kwargs["allow_headers"]
            
            # Verificar se as credenciais são permitidas
            assert "allow_credentials" in kwargs
            assert kwargs["allow_credentials"] == True
            
            # Verificar cabeçalhos expostos
            assert "expose_headers" in kwargs
            assert "X-RateLimit-Limit" in kwargs["expose_headers"]
            assert "X-RateLimit-Remaining" in kwargs["expose_headers"]
            assert "X-RateLimit-Reset" in kwargs["expose_headers"]
            assert "Retry-After" in kwargs["expose_headers"]
    
    def test_swagger_configuration(self, test_app):
        """Teste para verificar a configuração do Swagger"""
        # Verificar parâmetros do Swagger
        assert test_app.swagger_ui_parameters, "Parâmetros do Swagger UI não definidos"
        
        # Verificar redirecionamento OAuth2
        assert test_app.swagger_ui_oauth2_redirect_url, "URL de redirecionamento OAuth2 não definido"
        
        # Verificar inicialização OAuth
        assert test_app.swagger_ui_init_oauth, "Inicialização OAuth não definida"
        
        # Verificar tags do OpenAPI
        assert test_app.openapi_tags, "Tags OpenAPI não definidas"
    
    def test_exception_handlers_registration(self):
        """Teste para verificar o registro dos tratadores de exceção"""
        # Criar um mock para a aplicação
        app_mock = MagicMock()
        
        # Importar função de registro
        from src.presentation.exception.exception_handlers import register_exception_handlers
        
        # Registrar tratadores de exceção
        register_exception_handlers(app_mock)
        
        # Verificar se os tratadores foram registrados
        assert app_mock.exception_handler.call_count >= 2, "Nem todos os tratadores de exceção foram registrados" 