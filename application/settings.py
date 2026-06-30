import os
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from pydantic import model_validator
from pydantic_settings import BaseSettings

import logging

load_dotenv()


class Settings(BaseSettings):
    WRITE_DATABASE_URL: str
    READ_DATABASE_URL: str
    SENTRY_DSN: Optional[str] = None
    SENTRY_TRACE_SAMPLE_RATE: Optional[float] = 0.01
    RELEASE_TAG: Optional[str] = None
    ENVIRONMENT: str
    DATASETTE_URL: str
    DATASETTE_TILES_URL: Optional[str] = None
    TILES_URL: Optional[str] = None
    DATA_FILE_URL: str
    GA_MEASUREMENT_ID: Optional[str] = None
    SMARTLOOK_ID: Optional[str] = None
    OS_CLIENT_KEY: Optional[str] = None
    OS_CLIENT_SECRET: Optional[str] = None
    DB_POOL_SIZE: Optional[int] = 5
    DB_POOL_MAX_OVERFLOW: Optional[int] = 10
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_SECURE: bool = True

    @model_validator(mode="before")
    @classmethod
    def split_redis_host(cls, values):
        host = values.get("REDIS_HOST")
        if host and ":" in host:
            h, p = host.split(":")
            values["REDIS_HOST"] = h
            values["REDIS_PORT"] = int(p)
        return values


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
    logging.info(
        f"Settings loaded (environment={settings.ENVIRONMENT}, release={settings.RELEASE_TAG})"
    )
    return settings
