from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseSettings, PostgresDsn, HttpUrl

load_dotenv()


class Settings(BaseSettings):
    S3_HOISTED_BUCKET: HttpUrl
    S3_COLLECTION_BUCKET: HttpUrl
    WRITE_DATABASE_URL: PostgresDsn
    READ_DATABASE_URL: PostgresDsn
    SENTRY_DSN: Optional[str] = None
    ENVIRONMENT: str


@lru_cache()
def get_settings() -> Settings:
    return Settings()
