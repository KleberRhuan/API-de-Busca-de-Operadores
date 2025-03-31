import logging
from typing import List, Optional
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException
from src.application.exception.violation_exception import ViolationException
from src.presentation.exception.error_message_translator import get_translator
from src.application.exception.business_exception import BusinessException
from src.application.exception.rate_limit_exception import RateLimitExceededException
from src.presentation.exception.api_error import Violation, ApiError
from src.presentation.exception.api_error_type import ApiErrorType
from fastapi import status


logger = logging.getLogger("uvicorn.error")
def create_api_error_response(
        error_type: ApiErrorType,
        status_code: status,
        detail: str,
        user_message: str = None,
        violations: Optional[List[Violation]] = None
) -> JSONResponse:
    logger.error(f"{error_type.title}: {detail}, {user_message}, {violations}")

    api_error = ApiError(
        status=status_code,
        type=error_type.value,
        title=error_type.title,
        detail=detail,
        userMessage=user_message,
        violations=violations
    )

    return JSONResponse(
        status_code=status_code,
        content=api_error.model_dump(exclude_none=True)
    )

"""
@Author: Kleber Rhuan
@Description: Captura excecções HTTP e trata-as de forma unificada
"""
def register_exception_handlers(app):


    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        if exc.status_code == 404:
            return create_api_error_response(
                error_type=ApiErrorType.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND,
                detail="O recurso solicitado não foi encontrado.",
                user_message="O recurso que você está tentando acessar não existe."
            )

        if exc.status_code == 405:
            return create_api_error_response(
                error_type=ApiErrorType.METHOD_NOT_ALLOWED,
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                detail="O método HTTP usado não é permitido para este endpoint.",
                user_message="Método não permitido. Verifique a documentação da API."
            )
        
        return generic_exception_handler(request, exc)

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(request: Request, exc: RequestValidationError):
        """
        Trata erros de validação da requisição com informações detalhadas
        """
        translator = get_translator()
        violations = []
        
        for error in exc.errors():
            field_path = ".".join(str(loc) for loc in error["loc"])
            translated_message = translator.translate(error)
            violations.append(Violation(name=field_path, message=translated_message))

        return create_api_error_response(
            error_type=ApiErrorType.MESSAGE_NOT_READABLE,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Erro de validação nos parâmetros da requisição.",
            user_message="Um ou mais parâmetros estão inválidos. Verifique e tente novamente.",
            violations=violations
        )
    
    @app.exception_handler(BusinessException)
    async def business_exception_handler(request: Request, exc: BusinessException):
        return create_api_error_response(
            error_type=ApiErrorType.INVALID_PARAMETER,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail= str(exc)
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error("Erro interno não tratado", exc_info=exc)
    
        return create_api_error_response(
            error_type=ApiErrorType.SYSTEM_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno.",
            user_message="Ocorreu um erro interno no servidor, tente novamente e se o problema persistir, entre em contato com o administrador."
        )

    """
    * @Info: Como a aplicação não realiza persistência de dados,
    *        os erros originados pelo SQLAlchemy (ex.: violações de integridade,
    *        problemas operacionais, etc.) são tratados de forma genérica
    *        como erros técnicos do sistema.
    """
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        return await generic_exception_handler(request, exc)
    
    @app.exception_handler(RateLimitExceededException)
    async def rate_limit_exception_handler(request: Request, exc: RateLimitExceededException):
        
        # Criar resposta com cabeçalhos de rate limit
        response = create_api_error_response(
            error_type=ApiErrorType.RATE_LIMIT_EXCEEDED,
            status_code=429,
            detail=str(exc),
            user_message="Você excedeu o limite de requisições. Por favor, aguarde alguns instantes antes de tentar novamente."
        )
        
        # Adicionar cabeçalhos específicos para rate limiting
        response.headers["Retry-After"] = str(exc.reset_in)
        response.headers["X-RateLimit-Limit"] = str(exc.limit)
        response.headers["X-RateLimit-Remaining"] = "0"
        response.headers["X-RateLimit-Reset"] = str(exc.reset_in)
        
        return response
    
    @app.exception_handler(ViolationException)
    async def violation_exception_handler(request: Request, exc: ViolationException):
        return create_api_error_response(
            error_type=ApiErrorType.INVALID_PARAMETER,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
            violations=[exc.violation]
        )
    
    
    
    
