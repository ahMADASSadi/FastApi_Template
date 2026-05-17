from pathlib import Path
from typing import Literal, overload

from pydantic.networks import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings as _BaseSettings
from pydantic_settings import SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent
ENV_DIR = Path(BASE_DIR / "env")


class BaseSettings(_BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_DIR / ".env",
        case_sensitive=False,
        env_file_encoding="utf-8",
        extra="ignore",
    )


class HTTPSettings(BaseSettings):
    API_VERSION: str
    HOST: str
    PORT: int


class AppSettings(BaseSettings):
    APP_NAME: str
    DEBUG: bool


class DBSettings(BaseSettings):
    DATABASE_DSN: PostgresDsn
    MAX_CONNECTIONS: int
    MIN_CONNECTIONS: int
    MAX_OVERFLOW: int
    TIMEOUT: int


class JWTSettings(BaseSettings):
    ISSUER: str
    PUBLIC_KEY: str | None
    AUDIENCE: str | None


class RedisSettings(BaseSettings):
    REDIS_DSN: RedisDsn


SettingsName = Literal["db", "http", "app", "redis", "jwt"]


@overload
def get_setting(class_name: Literal["db"]) -> DBSettings: ...
@overload
def get_setting(class_name: Literal["http"]) -> HTTPSettings: ...
@overload
def get_setting(class_name: Literal["redis"]) -> RedisSettings: ...
@overload
def get_setting(class_name: Literal["app"]) -> AppSettings: ...
@overload
def get_setting(class_name: Literal["jwt"]) -> JWTSettings: ...


def get_setting(
    class_name: SettingsName,
) -> AppSettings | DBSettings | HTTPSettings | RedisSettings | JWTSettings | None:
    """Returns the existing settings' class else None"""
    return {
        "db": DBSettings(),
        "http": HTTPSettings(),
        "app": AppSettings(),
        "redis": RedisSettings(),
        "jwt": JWTSettings(),
    }.get(class_name)
