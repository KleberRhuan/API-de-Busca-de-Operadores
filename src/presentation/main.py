from fastapi import FastAPI
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
    uvicorn.run(application, host="0.0.0.0", port=8080, reload=True)