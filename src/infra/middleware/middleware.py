from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["localhost"],
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["Accept", "Content-Type"],
        expose_headers=[
            "X-RateLimit-Limit", 
            "X-RateLimit-Remaining", 
            "X-RateLimit-Reset", 
            "Retry-After"
        ],
    )
    return app