from dotenv import load_dotenv
from pydantic import BaseSettings, PostgresDsn
from pydantic.tools import lru_cache

load_dotenv()


class Settings(BaseSettings):
    DATASETTE_URL: str
    S3_COLLECTION_BUCKET: str
    WRITE_DATABASE_URL: PostgresDsn
    READ_DATABASE_URL: PostgresDsn


@lru_cache()
def get_settings() -> Settings:
    return Settings()
