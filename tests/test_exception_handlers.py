import pytest
from fastapi import FastAPI, status, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
from unittest.mock import patch, MagicMock, AsyncMock
from src.application.exception.business_exception import BusinessException
from src.application.exception.invalid_sort_parameter_exception import InvalidSortParameterException
from src.application.exception.rate_limit_exception import RateLimitExceededException
from src.presentation.exception.api_error_type import ApiErrorType
from src.application.exception.violation_exception import ViolationException

class TestExceptionHandlers:
    """Testes para verificar os manipuladores de exceção"""
    
    @pytest.fixture
    def mock_app(self):
        """Cria um mock da aplicação FastAPI"""
        app = MagicMock(spec=FastAPI)
        app.exception_handler = MagicMock()
        return app
    
    @pytest.fixture
    def mock_request(self):
        """Cria um mock de requisição para uso nos testes"""
        request = MagicMock(spec=Request)
        return request
    
    def test_register_exception_handlers(self, mock_app):
        """Testa se todos os tratadores de exceção são registrados corretamente"""
        from src.presentation.exception.exception_handlers import register_exception_handlers
        
        # Registrar tratadores de exceção
        register_exception_handlers(mock_app)
        
        # Verificar se os tratadores esperados foram registrados
        expected_exceptions = [
            StarletteHTTPException,
            RequestValidationError,
            BusinessException,
            ViolationException,  # InvalidSortParameterException é um tipo de ViolationException
            RateLimitExceededException,
            SQLAlchemyError,
            Exception  # Handler genérico
        ]
        
        # Contar quantos dos tratadores esperados foram registrados
        handler_calls = mock_app.exception_handler.call_args_list
        registered_exceptions = [args[0][0] for args in handler_calls]
        
        for exc in expected_exceptions:
            assert exc in registered_exceptions, f"Tratador para {exc.__name__} não foi registrado"
    
    async def test_http_exception_handler(self, mock_request):
        """Testa o tratador de exceções HTTP"""
        from src.presentation.exception.exception_handlers import register_exception_handlers
        
        # Criar app mockado com handlers reais
        app = FastAPI()
        register_exception_handlers(app)
        
        # Obter o handler HTTP
        handler = app.exception_handlers[StarletteHTTPException]
        
        # Testar para erro 404
        exception_404 = StarletteHTTPException(status_code=404)
        response_404 = await handler(mock_request, exception_404)
        
        # Verificar resposta
        assert response_404.status_code == 404
        data_404 = response_404.body
        assert b"RESOURCE_NOT_FOUND" in data_404
        
        # Testar para erro 405
        exception_405 = StarletteHTTPException(status_code=405)
        response_405 = await handler(mock_request, exception_405)
        
        # Verificar resposta
        assert response_405.status_code == 405
        data_405 = response_405.body
        assert b"METHOD_NOT_ALLOWED" in data_405
    
    async def test_validation_exception_handler(self, mock_request):
        """Testa o tratador de exceções de validação"""
        from src.presentation.exception.exception_handlers import register_exception_handlers
        
        # Criar app mockado com handlers reais
        app = FastAPI()
        register_exception_handlers(app)
        
        # Obter o handler de validação
        handler = app.exception_handlers[RequestValidationError]
        
        # Criar uma exceção de validação com erros
        errors = [
            {"loc": ("query", "name"), "msg": "field required", "type": "value_error.missing"},
            {"loc": ("query", "age"), "msg": "value is not a valid integer", "type": "type_error.integer"}
        ]
        exception = RequestValidationError(errors=errors)
        
        # Executar o handler
        response = await handler(mock_request, exception)
        
        # Verificar resposta
        assert response.status_code == 422
        data = response.body
        assert b"MESSAGE_NOT_READABLE" in data
        assert b"violations" in data
        assert b"name" in data
        assert b"age" in data
    
    async def test_business_exception_handler(self, mock_request):
        """Testa o tratador de exceções de negócio"""
        from src.presentation.exception.exception_handlers import register_exception_handlers
        
        # Criar app mockado com handlers reais
        app = FastAPI()
        register_exception_handlers(app)
        
        # Obter o handler de exceção de negócio
        handler = app.exception_handlers[BusinessException]
        
        # Criar uma exceção de negócio
        exception = BusinessException(
            error_type=ApiErrorType.BUSINESS_ERROR,
            detail="Erro de negócio",
            user_message="Ocorreu um erro de negócio"
        )
        
        # Executar o handler
        response = await handler(mock_request, exception)
        
        # Verificar resposta
        assert response.status_code == 400
        data = response.body
        assert b"BUSINESS_ERROR" in data
        assert b"Erro de neg" in data
    
    async def test_rate_limit_exception_handler(self, mock_request):
        """Testa o tratador de exceções de limite de requisições"""
        from src.presentation.exception.exception_handlers import register_exception_handlers
        
        # Criar app mockado com handlers reais
        app = FastAPI()
        register_exception_handlers(app)
        
        # Obter o handler de exceção de rate limit
        handler = app.exception_handlers[RateLimitExceededException]
        
        # Criar uma exceção de rate limit
        exception = RateLimitExceededException(
            limit=100,
            window=60,
            reset_in=30
        )
        
        # Executar o handler
        response = await handler(mock_request, exception)
        
        # Verificar resposta
        assert response.status_code == 429
        assert "retry-after" in response.headers
        assert response.headers["retry-after"] == "30"
        
        data = response.body
        assert b"TOO_MANY_REQUESTS" in data
        assert b"429" in data
    
    async def test_database_exception_handler(self, mock_request):
        """Testa o tratador de exceções de banco de dados"""
        from src.presentation.exception.exception_handlers import register_exception_handlers
        
        # Criar app mockado com handlers reais
        app = FastAPI()
        register_exception_handlers(app)
        
        # Obter o handler de exceção de banco de dados
        handler = app.exception_handlers[SQLAlchemyError]
        
        # Criar uma exceção de banco de dados
        exception = SQLAlchemyError("Erro no banco de dados")
        
        # Criar um patch para o logger para evitar logs de erro durante os testes
        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            # Executar o handler
            response = await handler(mock_request, exception)
            
            # Verificar se o erro foi logado
            assert mock_logger.error.called
        
        # Verificar resposta
        assert response.status_code == 500
        data = response.body
        assert b"INTERNAL_SERVER_ERROR" in data
        
        # A mensagem de erro original não deve ser exposta ao usuário
        assert b"Erro no banco de dados" not in data
    
    async def test_generic_exception_handler(self, mock_request):
        """Testa o tratador genérico de exceções"""
        from src.presentation.exception.exception_handlers import register_exception_handlers
        
        # Criar app mockado com handlers reais
        app = FastAPI()
        register_exception_handlers(app)
        
        # Obter o handler genérico
        handler = app.exception_handlers[Exception]
        
        # Criar uma exceção genérica
        exception = Exception("Erro inesperado")
        
        # Criar um patch para o logger para evitar logs de erro durante os testes
        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            # Executar o handler
            response = await handler(mock_request, exception)
            
            # Verificar se o erro foi logado
            assert mock_logger.error.called
        
        # Verificar resposta
        assert response.status_code == 500
        data = response.body
        assert b"INTERNAL_SERVER_ERROR" in data
        
        # A mensagem de erro original não deve ser exposta ao usuário
        assert b"Erro inesperado" not in data 
        
    async def test_invalid_sort_parameter_exception_handler(self, mock_request):
        """Testa o tratador de exceções para parâmetros de ordenação inválidos"""
        from src.presentation.exception.exception_handlers import register_exception_handlers
        
        # Criar app mockado com handlers reais
        app = FastAPI()
        register_exception_handlers(app)
        
        # Obter o handler de exceção de parâmetro de ordenação inválido
        handler = app.exception_handlers[InvalidSortParameterException]
        
        # Criar uma exceção de parâmetro de ordenação inválido
        exception = InvalidSortParameterException(
            field="sort_field",
            message="O campo de ordenação 'rating' não é válido"
        )
        
        # Executar o handler
        response = await handler(mock_request, exception)
        
        # Verificar resposta
        assert response.status_code == 422
        data = response.body
        assert b"INVALID_PARAMETER" in data
        
        # Verificar se tem informação de violation
        assert b"violations" in data
        assert b"sort_field" in data
        assert b"rating" in data 