import os
from aiocache import Cache
from aiocache.serializers import JsonSerializer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class DBManager:
    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.dbname = os.getenv("DB_NAME", "my_database")
        self.user = os.getenv("DB_USER", "my_user")
        self.password = os.getenv("DB_PASS", "my_password")
        self.port = os.getenv("DB_PORT", "5432")

        # Redis cache configuration
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", 6379))
        self.redis_password = os.getenv("REDIS_PASS", None)
        self.cache = Cache(
            Cache.REDIS,
            endpoint=self.redis_host,
            port=self.redis_port,
            password=self.redis_password,
            serializer=JsonSerializer()
        )

    def get_db(self) :
        engine = create_engine(f'postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}')
        session_local = sessionmaker(bind=engine)
        db = session_local()
        try:
            yield db
        finally:
            db.close()

    def get_cache(self):
        return self.cache