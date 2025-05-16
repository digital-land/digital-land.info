import os
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseSettings, PostgresDsn, HttpUrl

import logging

load_dotenv()


class Settings(BaseSettings):
    WRITE_DATABASE_URL: PostgresDsn
    READ_DATABASE_URL: PostgresDsn
    SENTRY_DSN: Optional[str] = None
    SENTRY_TRACE_SAMPLE_RATE: Optional[float] = 0.01
    RELEASE_TAG: Optional[str] = None
    ENVIRONMENT: str
    DATASETTE_URL: HttpUrl
    DATASETTE_TILES_URL: Optional[HttpUrl]
    DATA_FILE_URL: HttpUrl
    GA_MEASUREMENT_ID: Optional[str] = None
    OS_CLIENT_KEY: Optional[str] = None
    OS_CLIENT_SECRET: Optional[str] = None
    DB_POOL_SIZE: Optional[int] = 5
    DB_POOL_MAX_OVERFLOW: Optional[int] = 10
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_SECURE: bool = True


@lru_cache()
def get_settings() -> Settings:
    # TODO remove as Gov PaaS is no longer needed
    # Gov.uk PaaS provides a URL to the postgres instance it provisions via DATABASE_URL
    # See https://docs.cloud.service.gov.uk/deploying_services/postgresql/#connect-to-a-postgresql-service-from-your-app
    settings = None
    if "DATABASE_URL" in os.environ:
        database_url = os.environ["DATABASE_URL"].replace(
            "postgres://", "postgresql://", 1
        )
        settings = Settings(
            READ_DATABASE_URL=database_url, WRITE_DATABASE_URL=database_url
        )
    else:
        settings = Settings()
    logging.info(f"Settings: {settings}")
    return settings
