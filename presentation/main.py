from fastapi import FastAPI, Depends, APIRouter
from application.services.operator_service import OperatorSearchService
from fastapi.responses import JSONResponse
import infra.config as config
from infra.db_manager import DBManager
from presentation.model.pageable_response import PageableResponse
from presentation.model.operator_request_params import OperatorRequestParams
from presentation.exception.exception_handlers import register_exception_handlers
from domain.repository.operator_repository import OperatorRepository

def create_application():
    app = FastAPI(
        title="API de Busca de Operadores",
        description="API para busca de operadores com base em parâmetros de busca. Teste Tecnico Intuitive Care",
        version="1.0.0"
    )
    config.load_env()
    register_exception_handlers(app)

    db_manager = DBManager()
    operator_repository = OperatorRepository(Depends(db_manager.get_db()))
    operator_search_service = OperatorSearchService(operator_repository)
    api_router = APIRouter(prefix="/api/v1")

    @api_router.get("/operators", response_class=JSONResponse)
    async def search_operators(params: OperatorRequestParams = Depends()) -> 'PageableResponse':
        return await operator_search_service.find_all_cached(params)

    if config.get_current_env() == "dev":
        @api_router.get("/cache-test", response_class=JSONResponse)
        async def cache_test():
            cache = db_manager.get_cache()
            key = "cache_test_key"
            test_value = {"message": "Cache is working!"}

            await cache.set(key, test_value, ttl=60)
            cached_value = await cache.get(key)
            return {"status": "success", "cached_value": cached_value}
   
    app.include_router(api_router)
    return app

application = create_application()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(application, host="0.0.0.0", port=8080, reload=True)