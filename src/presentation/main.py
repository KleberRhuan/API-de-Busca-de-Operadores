from fastapi import FastAPI
import os
from src.infra.config import setup_application
from src.presentation.api.routes import get_router

def create_application():
    # Criar a aplicação FastAPI
    app = FastAPI()
    
    # Configurar a aplicação
    app = setup_application(app)
    
    # Registrar as rotas
    app.include_router(get_router())
    
    return app

application = create_application()

if __name__ == '__main__':
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8080))
    
    uvicorn.run(application, host=host, port=port, reload=True)