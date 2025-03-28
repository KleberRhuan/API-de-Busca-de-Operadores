from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from presentation.model.operator_request_params import OperatorRequestParams
from infra.swagger_config import ENDPOINT_CONFIG as SWAGGER_CONFIG
from infra.limiter_config import limiter
from presentation.api.dependencies import get_operator_service, get_db_manager
import infra.config as config

api_router = APIRouter(prefix="/api/v1")

@api_router.get(
    "/operators", 
    response_model=SWAGGER_CONFIG["operators"]["response_model"],
    tags=[SWAGGER_CONFIG["operators"]["tag"]],
    summary=SWAGGER_CONFIG["operators"]["summary"],
    description=SWAGGER_CONFIG["operators"]["description"],
    response_description=SWAGGER_CONFIG["operators"]["response_description"],
    responses=SWAGGER_CONFIG["operators"]["responses"]
)
@limiter.limit("100/minute")
async def search_operators(
    params: OperatorRequestParams = Depends(),
    operator_service = Depends(get_operator_service)
):
    return await operator_service.find_all_cached(params)

# Endpoint condicional para ambiente de desenvolvimento
if config.get_current_env() == "dev":
    @api_router.get(
        "/cache-test", 
        response_class=JSONResponse,
        tags=[SWAGGER_CONFIG["cache_test"]["tag"]],
        summary=SWAGGER_CONFIG["cache_test"]["summary"],
        description=SWAGGER_CONFIG["cache_test"]["description"],
        responses=SWAGGER_CONFIG["cache_test"]["responses"]
    )
    async def cache_test(db_manager = Depends(get_db_manager)):
        cache = db_manager.get_cache()
        key = "cache_test_key"
        test_value = {"message": "Cache is working!"}

        await cache.set(key, test_value, ttl=60)
        cached_value = await cache.get(key)
        return {"status": "success", "cached_value": cached_value}

def get_router():
    return api_router