import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente em ambientes de desenvolvimento
if os.getenv("ENV", "dev") != "prod":
    load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from aiocache import Cache
from aiocache.serializers import JsonSerializer
import redis

# Configuração do banco de dados
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "my_database")
DB_USER = os.getenv("DB_USER", "my_user")
DB_PASS = os.getenv("DB_PASS", "my_password")
DB_PORT = os.getenv("DB_PORT", "5432")

DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Inicialização do SQLAlchemy sem mod no pool de conexoes
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Configuração do Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASS = os.getenv("REDIS_PASS", None)
REDIS_URL = f"redis://{':'+REDIS_PASS+'@' if REDIS_PASS else ''}{REDIS_HOST}:{REDIS_PORT}/0"


def get_redis_connection():
    try:
        return redis.from_url(REDIS_URL)
    except Exception as e:
        print(f"Erro ao conectar ao Redis: {e}")
        return None

# Inicialização do cache
cache = Cache(
    Cache.REDIS,
    endpoint=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASS,
    serializer=JsonSerializer()
)

# Função para injeção de dependência
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_cache():
    return cache

# Exportar as funções/objetos principais
__all__ = ['engine', 'SessionLocal', 'get_db', 'get_cache', 'cache', 'get_redis_connection', 'REDIS_URL']