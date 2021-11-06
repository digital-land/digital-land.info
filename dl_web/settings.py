from dotenv import find_dotenv, load_dotenv
from pydantic import BaseSettings
from pydantic.tools import lru_cache

dotenv_file = find_dotenv(".env.shared")
load_dotenv(dotenv_file)


class Settings(BaseSettings):
    DATASETTE_URL: str
    S3_COLLECTION_BUCKET: str


@lru_cache()
def get_settings() -> Settings:
    return Settings()
