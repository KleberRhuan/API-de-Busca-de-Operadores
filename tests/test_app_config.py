import os
from unittest.mock import MagicMock, patch

import pytest
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

    def test_environment_config(self):
        """Teste para verificar se as variáveis de ambiente são carregadas corretamente"""
        # Importar configurações aqui em vez de usar self.app_settings
        from src.infra.config.config import get_app_url

        # Verificar o valor atual da base_url (0.0.0.0 em vez de 127.0.0.1)
        assert get_app_url() == "http://0.0.0.0:8080"

    def test_rate_limit_configuration(self):
        """Teste para verificar se a configuração de rate limit é aplicada corretamente"""
        # Valores de configuração
        rate_limit = 100
        rate_window = 60

        # Simular ambiente com valores configurados
        with patch.dict(
            os.environ, {"RATE_LIMIT": str(rate_limit), "RATE_WINDOW": str(rate_window)}
        ):
            # Criar um mock para a aplicação
            app_mock = MagicMock()

            # Importar função de configuração
            from src.infra.config.config import setup_application

            # Configurar a aplicação
            setup_application(app_mock)

            # Verificar se o middleware foi adicionado
            app_mock.add_middleware.assert_called()

    def test_cors_configuration(self):
        """Teste para verificar se a configuração CORS é aplicada corretamente"""
        # Criar um mock para a aplicação
        app_mock = MagicMock()

        # Importar função de configuração
        from src.infra.middleware.cors_middleware import setup_cors

        # Configurar CORS
        setup_cors(app_mock)

        # Verificar se add_middleware foi chamado
        app_mock.add_middleware.assert_called_once()

        # Extrair argumentos da chamada
        args, kwargs = app_mock.add_middleware.call_args

        # Verificar origens permitidas
        assert "allow_origins" in kwargs
        assert any(
            "localhost" in origin for origin in kwargs["allow_origins"]
        ), f"Nenhuma origem contém 'localhost': {kwargs['allow_origins']}"

        # Verificar métodos permitidos
        assert "allow_methods" in kwargs
        assert "GET" in kwargs["allow_methods"]

        # Verificar cabeçalhos permitidos
        assert "allow_headers" in kwargs
        assert "Content-Type" in kwargs["allow_headers"]

        # Verificar se as credenciais são permitidas
        assert "allow_credentials" in kwargs
        assert kwargs["allow_credentials"] == False

        # Verificar cabeçalhos expostos
        assert "expose_headers" in kwargs
        assert "X-RateLimit-Limit" in kwargs["expose_headers"]
        assert "X-RateLimit-Remaining" in kwargs["expose_headers"]
        assert "X-RateLimit-Reset" in kwargs["expose_headers"]
        assert "Retry-After" in kwargs["expose_headers"]

    def test_swagger_configuration(self, test_app):
        """Teste para verificar a configuração do Swagger"""
        # Verificar configurações OpenAPI
        openapi_schema = test_app.openapi()
        assert openapi_schema, "Schema OpenAPI não gerado"
        assert (
            "info" in openapi_schema
        ), "Informações básicas não definidas no schema OpenAPI"
        assert (
            "title" in openapi_schema["info"]
        ), "Título não definido no schema OpenAPI"
        assert (
            "version" in openapi_schema["info"]
        ), "Versão não definida no schema OpenAPI"

    def test_exception_handlers_registration(self):
        """Teste para verificar o registro dos tratadores de exceção"""
        # Criar um mock para a aplicação
        app_mock = MagicMock()

        # Importar função de registro
        from src.presentation.exception.exception_handlers import \
            register_exception_handlers

        # Registrar tratadores de exceção
        register_exception_handlers(app_mock)

        # Verificar se os tratadores foram registrados (pelo menos 6 baseados no código)
        assert (
            app_mock.exception_handler.call_count >= 6
        ), "Nem todos os tratadores de exceção foram registrados"
