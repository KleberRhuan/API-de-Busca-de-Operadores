import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app: FastAPI) -> FastAPI:
    """
    Configura o middleware CORS para a aplicação FastAPI.

    O FastAPI e Starlette implementam suporte a requisições OPTIONS,
    mas para que funcionem corretamente, os clientes precisam incluir
    os cabeçalhos 'Origin' e 'Access-Control-Request-Method' nas requisições.

    Parâmetros:
        app: Instância do FastAPI a ser configurada

    Retorna:
        A instância do FastAPI configurada com o middleware CORS
    """
    allow_origins = os.getenv("CORS_ORIGIN", "http://localhost:5173").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=False,
        allow_methods=["GET", "OPTIONS"],
        allow_headers=["Accept", "Content-Type"],
        expose_headers=[
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
            "Retry-After",
        ],
    )
    return app
