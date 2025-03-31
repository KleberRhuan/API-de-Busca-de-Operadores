from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from aiocache import Cache, caches
import src.infra.config as config
from src.application.service.operator_service import OperatorService
from src.infra.config.swagger_config import ENDPOINT_CONFIG as SWAGGER_CONFIG
from src.infra.database import get_db
from src.presentation.model.operator_request_params import \
    OperatorRequestParams

api_router = APIRouter(prefix="/api/v1")

# Função para injeção de dependência do OperatorService
def get_operator_service(db=Depends(get_db)):
    return OperatorService(db)

@api_router.get("/health")
def health():
    return {"status": "ok"}

@api_router.get(
    "/operators",
    response_model=SWAGGER_CONFIG["operators"]["response_model"],
    tags=[SWAGGER_CONFIG["operators"]["tag"]],
    summary=SWAGGER_CONFIG["operators"]["summary"],
    description=SWAGGER_CONFIG["operators"]["description"],
    response_description=SWAGGER_CONFIG["operators"]["response_description"],
    responses=SWAGGER_CONFIG["operators"]["responses"],
)
async def search_operators(
    params: OperatorRequestParams = Depends(),
    operator_service: OperatorService = Depends(get_operator_service),
):
    return await operator_service.find_all_cached(params)


# Endpoint condicional para ambiente de desenvolvimento
if config.get_current_env() == "dev":

    @api_router.get(
        "/cache-tests",
        response_class=JSONResponse,
        tags=[SWAGGER_CONFIG["cache_test"]["tag"]],
        summary=SWAGGER_CONFIG["cache_test"]["summary"],
        description=SWAGGER_CONFIG["cache_test"]["description"],
        responses=SWAGGER_CONFIG["cache_test"]["responses"],
    )
    async def cache_test():
        cache = caches.get("default")
        key = "cache_test_key"
        test_value = {"message": "Cache is working!"}

        await cache.set(key, test_value, ttl=60)
        cached_value = await cache.get(key)
        return {"status": "success", "cached_value": cached_value}


def get_router():
    return api_router
