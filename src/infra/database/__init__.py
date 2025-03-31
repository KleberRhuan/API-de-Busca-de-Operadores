import logging
import os

from dotenv import load_dotenv

# Carrega as variáveis de ambiente em ambientes de desenvolvimento
if os.getenv("ENV", "dev") != "prod":
    load_dotenv()

import redis
from aiocache import Cache, RedisCache, caches
from aiocache.serializers import JsonSerializer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

# Configuração do banco de dados
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/operators_db"
)

# Inicialização do SQLAlchemy
engine = create_engine(
    DATABASE_URL, pool_pre_ping=True, pool_recycle=3600, pool_size=10, max_overflow=20
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Configuração do Redis
# URL para conexão com o Redis
REDIS_HOST = os.getenv("REDIS_HOST", "redis")  # "redis" é o nome do serviço no Docker
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# Configuração global para aiocache
caches.set_config({
    'default': {
        'cache': "aiocache.RedisCache",
        'endpoint': "localhost",
        'port': REDIS_PORT,
        'db': REDIS_DB,
        'serializer': {
            'class': "aiocache.serializers.JsonSerializer"
        }
    }
})

def get_redis_connection():

    try:
        return redis.from_url(REDIS_URL)
    except Exception as e:
        logger.error(f"Erro ao conectar ao Redis: {e}")
        return None

redis_instance = get_redis_connection()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

__all__ = [
    "engine",
    "SessionLocal",
    "get_db",
    "get_redis_connection",
    "REDIS_URL",
]
