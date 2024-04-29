from pathlib import Path, PosixPath
from typing import List, Union, Tuple, Type, Callable, Optional, Any

from pydantic import field_validator, PostgresDsn
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BASE_DIR: PosixPath = Path(__file__).resolve(strict=True).parent.parent.parent

    APP_DIR: PosixPath = BASE_DIR / "dns_system"

    API_ROUTE_STR: str = "/api"
    CURRENT_API_VERSION: str = "/v1"

    SERVER_NAME: str = "DNS_SYSTEM"
    SECRET_KEY: str = "dCy4s0iiNeE3NnLIKwEqcgsDZFJ4UCVs"

    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str = "DNS System"

    USE_TZ: bool = True
    TZ: str = "Asia/Bishkek"

    EXCEPTIONS_TO_HANDLE: List[Tuple[Type[Exception], Callable]] = []

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "ikyol"
    POSTGRES_PASSWORD: str = "1"
    POSTGRES_DB: str = "dns_system"
    POSTGRES_PORT: int = 5432

    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 15
    DB_POOL_RECYCLE: int = 3600

    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: Optional[str], values: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=values.data.get("POSTGRES_SERVER"),
            path=values.data.get("POSTGRES_DB") or "",
            port=values.data.get("POSTGRES_PORT"),
        )

    DSN: str = ""

    CLOUDFLARE_API_KEY: str = "QHQs7rGBEGtm2QJDRrN6zmxi8jTYdXL7RfYe6T4k"
    CLOUDFLARE_ACCOUNT_ID: str = "564d4d39f4d89544c9f503b996f4079a"
    CLOUDFLARE_API: str = "https://api.cloudflare.com/client/v4/zones"

    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore"
    )


settings = Settings()
