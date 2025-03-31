import os

from fastapi import FastAPI
from limits.storage import MemoryStorage, RedisStorage

from src.infra.config.swagger_config import configure_swagger
from src.infra.database import get_redis_connection
from src.infra.middleware.cors_middleware import setup_cors
from src.infra.middleware.rate_limit_middleware import RateLimitMiddleware
from src.presentation.exception.exception_handlers import \
    register_exception_handlers


def get_current_env():
    return os.getenv("ENV", "dev")


def get_app_url():
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8080))
    return f"http://{host}:{port}"


class Config:
    orm_mode = True
    allow_population_by_field_name = True

    @staticmethod
    def app_url():
        return get_app_url()

def setup_application(app: FastAPI) -> FastAPI:
    # Configurar CORS
    setup_cors(app)

    # Configurar rate limiter
    rate_limit = int(os.getenv("RATE_LIMIT", "100"))
    rate_window = int(os.getenv("RATE_WINDOW", "60"))

    # Obter conexão Redis compartilhada do módulo database
    redis_instance = get_redis_connection()

    # Escolher o armazenamento para o rate limiter
    if redis_instance:
        try:
            storage = RedisStorage(redis_instance)
        except Exception:
            storage = MemoryStorage()
    else:
        storage = MemoryStorage()

    # Adicionar o middleware de rate limiting
    app.add_middleware(
        RateLimitMiddleware, limit=rate_limit, window=rate_window, storage=storage
    )

    # Configurar Swagger
    configure_swagger(app)

    # Registrar tratadores de exceção
    register_exception_handlers(app)

    return app
