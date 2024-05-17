import os
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseSettings, PostgresDsn, HttpUrl

load_dotenv()


class Settings(BaseSettings):
    WRITE_DATABASE_URL: PostgresDsn
    READ_DATABASE_URL: PostgresDsn
    SENTRY_DSN: Optional[str] = None
    SENTRY_TRACE_SAMPLE_RATE: Optional[float] = 0.01
    RELEASE_TAG: Optional[str] = None
    ENVIRONMENT: str
    DATASETTE_URL: HttpUrl
    DATA_FILE_URL: HttpUrl
    GA_MEASUREMENT_ID: Optional[str] = None
    OS_CLIENT_KEY: Optional[str] = None
    OS_CLIENT_SECRET: Optional[str] = None


@lru_cache()
def get_settings() -> Settings:
    # TODO remove as Gov PaaS is no longer needed
    # Gov.uk PaaS provides a URL to the postgres instance it provisions via DATABASE_URL
    # See https://docs.cloud.service.gov.uk/deploying_services/postgresql/#connect-to-a-postgresql-service-from-your-app

    if "DATABASE_URL" in os.environ:
        database_url = os.environ["DATABASE_URL"].replace(
            "postgres://", "postgresql://", 1
        )
        return Settings(READ_DATABASE_URL=database_url, WRITE_DATABASE_URL=database_url)
    else:
        return Settings()
