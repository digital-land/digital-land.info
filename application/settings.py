import os
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
    # Gov.uk PaaS provides a URL to the postgres instance it provisions via DATABASE_URL
    # See https://docs.cloud.service.gov.uk/deploying_services/postgresql/#connect-to-a-postgresql-service-from-your-app
    if "DATABASE_URL" in os.environ:
        return Settings(
            READ_DATABASE_URL=os.environ["DATABASE_URL"],
            WRITE_DATABASE_URL=os.environ["DATABASE_URL"],
        )
    else:
        return Settings()
