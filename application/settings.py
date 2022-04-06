from dotenv import load_dotenv
from pydantic import BaseSettings, PostgresDsn, HttpUrl
from pydantic.tools import lru_cache

load_dotenv()


class Settings(BaseSettings):
    S3_HOISTED_BUCKET: HttpUrl
    S3_COLLECTION_BUCKET: HttpUrl
    WRITE_DATABASE_URL: PostgresDsn
    READ_DATABASE_URL: PostgresDsn


@lru_cache()
def get_settings() -> Settings:
    return Settings()
