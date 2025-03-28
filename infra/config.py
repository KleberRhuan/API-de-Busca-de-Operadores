import os
from dotenv import load_dotenv
from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from infra.swagger_config import configure_swagger
import infra.config as config
from presentation.exception.exception_handlers import register_exception_handlers
from infra.middleware import setup_cors
from infra.limiter_config import limiter

def load_env():
    if os.getenv("ENV", "dev") != "prod":
        load_dotenv()


def get_current_env():
    return os.getenv("ENV", "dev")


class Config:
    orm_mode = True
    allow_population_by_field_name = True
    APP_URL = os.getenv("APP_URL", "http://127.0.0.1:8080")


def setup_application(app: FastAPI) -> FastAPI:
    # Configurar CORS
    setup_cors(app)
    
    # Configurar rate limiter
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # Configurar Swagger
    configure_swagger(app)
    
    # Carregar variáveis de ambiente
    load_env()
    
    # Registrar tratadores de exceção
    register_exception_handlers(app)
    
    return app