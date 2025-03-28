import logging
from typing import List, Optional
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException
from application.exception.business_exception import BusinessException
from presentation.exception.api_error import Violation, ApiError
from slowapi.errors import RateLimitExceeded
from presentation.exception.api_error_type import ApiErrorType

def create_api_error_response(
        error_type: ApiErrorType,
        status_code: int,
        detail: str,
        user_message: str = None,
        violations: Optional[List[Violation]] = None
) -> JSONResponse:

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

    logger = logging.getLogger("uvicorn.error")
    
    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        logger.info(f"RateLimitExceeded: {exc}")
        limit = getattr(exc, "limit", "")
        remaining = getattr(exc, "headers", {}).get("X-RateLimit-Remaining", "0")
        reset = getattr(exc, "headers", {}).get("X-RateLimit-Reset", "")
        
        detail = f"Limite de requisições excedido. Limite: {limit}, Restantes: {remaining}, Reinicia em: {reset}s."
        
        return create_api_error_response(
            error_type=ApiErrorType.RATE_LIMIT_EXCEEDED,
            status_code=429,
            detail=detail,
            user_message="Você excedeu o limite de requisições permitido. Por favor, aguarde um momento antes de tentar novamente."
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        if exc.status_code == 404:
            return create_api_error_response(
                error_type=ApiErrorType.RESOURCE_NOT_FOUND,
                status_code=404,
                detail="O recurso solicitado não foi encontrado.",
                user_message="O recurso que você está tentando acessar não existe."
            )

        if exc.status_code == 405:
            return create_api_error_response(
                error_type=ApiErrorType.METHOD_NOT_ALLOWED,
                status_code=405,
                detail="O método HTTP usado não é permitido para este endpoint.",
                user_message="Método não permitido. Verifique a documentação da API."
            )
        
        return generic_exception_handler(request, exc)

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(request: Request, exc: RequestValidationError):
        """
        Trata erros de validação da requisição com informações detalhadas
        """
        violations = [
            Violation(
                name=".".join(str(loc) for loc in error["loc"]),
                message=error["msg"]
            )
            for error in exc.errors()
        ]

        return create_api_error_response(
            error_type=ApiErrorType.MESSAGE_NOT_READABLE,
            status_code=422,
            detail="Erro de validação nos parâmetros da requisição.",
            user_message="Um ou mais parâmetros estão inválidos. Verifique e tente novamente.",
            violations=violations
        )
    
    @app.exception_handler(BusinessException)
    async def invalid_order_parameter_handler(request: Request, exc: BusinessException):
        return create_api_error_response(
            error_type=ApiErrorType.INVALID_PARAMETER,
            status_code=400,
            detail= str(exc)
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error("Erro interno não tratado", exc_info=exc)
    
        return create_api_error_response(
            error_type=ApiErrorType.SYSTEM_ERROR,
            status_code=500,
            detail=f"Erro interno: {str(exc)}",
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