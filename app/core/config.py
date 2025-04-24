import logging
import os
import secrets
from pathlib import Path
from typing import Any, List, Optional, Union

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, PostgresDsn, field_validator, RedisDsn
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):

    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str = "TeleGenius Pro"
    PROJECT_DESCRIPTION: str = "TeleGenius Pro API"
    VERSION: str = "0.1.0"

    # env config
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = ENV == "development"

    # PostgreSQL config
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432
    SQLMODEL_DATABASE_URI: Optional[PostgresDsn] = None

    # deepl config
    DEEPL_API_KEY: str = os.getenv("DEEPL_API_KEY")
    LANGUAGE: str = os.getenv("LANGUAGE", "en-US")

    # # Redis config
    REDIS_USER: str | None
    REDIS_PASSWORD: str | None
    REDIS_HOST: str
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: Optional[RedisDsn] = None

    @field_validator("REDIS_URL", mode="before")
    def assemble_redis_url(cls, v: Optional[str], info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        try:
            data = info.data
            return RedisDsn.build(
                scheme="redis",
                username=data.get("REDIS_USER"),
                password=data.get("REDIS_PASSWORD"),
                host=data.get("REDIS_HOST"),
                port=data.get("REDIS_PORT"),
                path=f"{data.get('REDIS_DB') or ''}",
            )
        except Exception as e:
            logging.error(f"Redis Connection configuration error: {e}")
            raise ValueError(
                "Redis Connection configuration error，Please check the environment variables"
            )

    @field_validator("SQLMODEL_DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: Optional[str], info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        try:
            data = info.data
            return PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=data.get("POSTGRES_USER"),
                password=data.get("POSTGRES_PASSWORD"),
                host=data.get("POSTGRES_SERVER"),
                port=data.get("POSTGRES_PORT"),
                path=f"{data.get('POSTGRES_DB') or ''}",
            )
        except Exception as e:
            logging.error(f"The database connection configuration is incorrect: {e}")
            raise ValueError(
                "The database connection configuration is incorrect，Please check the environment variables"
            )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Check whether the.env file exists
env_path = Path(".env")
if not env_path.exists():
    raise FileNotFoundError(
        ".env file was not found. Please create .env file and configure the necessary environment variables"
    )

settings = Settings()
