from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseSettings, PostgresDsn
from pydantic.tools import lru_cache

load_dotenv()


class Settings(BaseSettings):
    DATASETTE_URL: Optional[str]
    S3_COLLECTION_BUCKET: Optional[str]
    WRITE_DATABASE_URL: Optional[PostgresDsn]
    READ_DATABASE_URL: Optional[PostgresDsn]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
