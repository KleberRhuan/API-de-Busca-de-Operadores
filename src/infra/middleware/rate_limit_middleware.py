from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from limits.storage import MemoryStorage
from limits.strategies import MovingWindowRateLimiter
from limits import RateLimitItemPerSecond
import time
import logging
from typing import Callable, Awaitable, Any
from src.application.exception.rate_limit_exception import RateLimitExceededException

logger = logging.getLogger("rate_limiter")

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: Callable,
        limit: int = 100,
        window: int = 60,
        storage: MemoryStorage = None
    ):
        super().__init__(app)
        self.storage = storage or MemoryStorage()
        self.limiter = MovingWindowRateLimiter(self.storage)
        self.limit = limit
        self.window = window
        logger.info(f"Rate limiter inicializado: limite={limit} por {window}s, storage={type(storage).__name__}")

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Any]]) -> Any:
        path = request.url.path
        
        # Não aplicar rate limiting à documentação e healthcheck
        if path in ["/docs", "/redoc", "/openapi.json", "/health"]:
            return await call_next(request)
        
        client_ip = self._get_client_identifier(request)
            
        # Criar chave única para este endpoint/IP (usando apenas a parte principal do caminho)
        # Exemplo: /api/v1/operators?page=1 -> /api/v1/operators
        endpoint = path.split('?')[0]
        namespace = endpoint.replace('/', '_').strip('_')
        
        key = f"{namespace}:{client_ip}"
        rate_limit_item = RateLimitItemPerSecond(self.limit, self.window)
        
        # Verificar se o cliente está dentro do limite
        is_allowed = self.limiter.test(rate_limit_item, key)
        
        if not is_allowed:
            reset_in = self._calculate_reset_time()
            logger.info(f"Rate limit excedido: {client_ip} em {endpoint}, reset em {reset_in}s")
            
            raise RateLimitExceededException(
                limit=self.limit,
                window=self.window,
                reset_in=reset_in
            )
        
        self.limiter.hit(rate_limit_item, key)
    
        response = await call_next(request)
        
        # Adicionar cabeçalhos de rate limit
        current = self.storage.get(rate_limit_item.key_for(key)) or 0
        remaining = max(0, self.limit - current)
        reset_in = self._calculate_reset_time()
        
        response.headers["X-RateLimit-Limit"] = str(self.limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_in)
        
        return response
    
    @staticmethod
    def _get_client_identifier(request: Request) -> str:
        """
        Extrai um identificador único para o cliente, considerando
        cabeçalhos de proxy e configurações de balanceamento.
        """
        
        for header in ["X-Real-IP", "X-Forwarded-For", "CF-Connecting-IP"]:
            if header in request.headers:
                # Para X-Forwarded-For, pegar o primeiro IP (mais à esquerda)
                if header == "X-Forwarded-For":
                    return request.headers[header].split(",")[0].strip()
                return request.headers[header]
        
        # Fallback para o IP de conexão direta
        client_host = getattr(request, "client", None)
        if client_host and hasattr(client_host, "host"):
            return request.client.host
        
        # Último recurso se não conseguir determinar
        return "unknown-client"
    
    def _calculate_reset_time(self) -> int:
        now = int(time.time())
        return self.window - (now % self.window) 