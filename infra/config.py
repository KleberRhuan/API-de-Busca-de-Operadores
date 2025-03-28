import os
from dotenv import load_dotenv

def load_env():
    if os.getenv("ENV", "dev") != "prod":
        load_dotenv()


def get_current_env():
    return os.getenv("ENV", "dev")


class Config:
    orm_mode = True
    allow_population_by_field_name = True
    APP_URL = os.getenv("APP_URL", "http://127.0.0.1:8080")
