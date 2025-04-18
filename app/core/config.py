import os
import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, field_validator
import logging
from pathlib import Path


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
    
    # 环境设置
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = ENV == "development"
    
    # PostgreSQL配置
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str = "5432"
    SQLMODEL_DATABASE_URI: Optional[PostgresDsn] = None

    @field_validator("SQLMODEL_DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        try:
            return PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=values.get("POSTGRES_USER"),
                password=values.get("POSTGRES_PASSWORD"),
                host=values.get("POSTGRES_SERVER"),
                port=values.get("POSTGRES_PORT"),
                path=f"/{values.get('POSTGRES_DB') or ''}",
            )
        except Exception as e:
            logging.error(f"数据库连接配置错误: {e}")
            raise ValueError("数据库连接配置错误，请检查环境变量")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 检查.env文件是否存在
env_path = Path(".env")
if not env_path.exists():
    raise FileNotFoundError("未找到.env文件，请创建.env文件并配置必要的环境变量")

settings = Settings()