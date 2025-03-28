import logging
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente em ambientes de desenvolvimento
if os.getenv("ENV", "dev") != "prod":
    load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from aiocache import Cache, RedisCache
from aiocache.serializers import JsonSerializer
import redis

logger = logging.getLogger(__name__)

# Configuração do banco de dados
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/operators_db")

# Inicialização do SQLAlchemy
engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True,
    pool_recycle=3600,  
    pool_size=10,        
    max_overflow=20  
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Configuração do Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

def get_redis_connection():
    try:
        return redis.from_url(REDIS_URL)
    except Exception as e:
        logger.error(f"Erro ao conectar ao Redis: {e}")
        return None

# Inicialização do cache
redis_instance = get_redis_connection()
if redis_instance:
    try:
        # Parse URL para configuração do Redis
        redis_parts = REDIS_URL.replace("redis://", "").split(":")
        host = redis_parts[0]
        port = int(redis_parts[1].split("/")[0])
        db = int(redis_parts[1].split("/")[1]) if len(redis_parts[1].split("/")) > 1 else 0
        
        cache = RedisCache(
            endpoint=host,
            port=port,
            db=db,
            serializer=JsonSerializer()
        )
        logger.info(f"Cache Redis inicializado com sucesso: {host}:{port}/{db}")
    except Exception as e:
        logger.error(f"Erro ao inicializar o cache Redis: {e}. Usando cache em memória.")
        cache = Cache(Cache.MEMORY, serializer=JsonSerializer())
else:
    # Fallback para cache em memória se o Redis não estiver disponível
    logger.warning("Redis não disponível. Usando cache em memória.")
    cache = Cache(Cache.MEMORY, serializer=JsonSerializer())

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_cache():
    return cache

__all__ = ['engine', 'SessionLocal', 'get_db', 'get_cache', 'cache', 'get_redis_connection', 'REDIS_URL']