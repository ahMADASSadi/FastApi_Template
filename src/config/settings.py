from pathlib import Path
from typing import Literal, overload

from pydantic.networks import AmqpDsn, PostgresDsn, RedisDsn
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
    VERSION: str

    @property
    def OPENAPI(self) -> dict:
        return {
            "title": f"{self.APP_NAME.title()} API",
            "version": self.VERSION,
            "description": "API documentation for Sepehr backend service.",
            "contact": {"name": "Sepehr Support", "email": "support@sepehr.com"},
        }


class DBSettings(BaseSettings):
    DATABASE_ASYNC_URL: PostgresDsn
    MAX_CONNECTIONS: int
    MIN_CONNECTIONS: int
    MAX_OVERFLOW: int
    TIMEOUT: int


class RedisSettings(BaseSettings):
    REDIS_DSN: RedisDsn


class AsyncTasQSettings(BaseSettings):
    ASYNCTASQ_DRIVER: str
    ASYNCTASQ_TASK_DEFAULTS_QUEUE: str
    ASYNCTASQ_TASK_DEFAULTS_RETRY: bool
    ASYNCTASQ_BROKER_URL: RedisDsn | AmqpDsn
    ASYNCTASQ_TASK_DEFAULTS_RETRY_POLICY: dict
    ASYNCTASQ_RESULT_BACKEND_URL: RedisDsn| AmqpDsn


class SecuritySettings(BaseSettings):
    ALLOWED_ORIGINS: list[str]
    ALLOWED_METHODS: list[str]
    ALLOWED_HEADERS: list[str]
    ALLOWED_HOSTS: list[str]


SettingsName = Literal["db", "http", "app", "redis", "security", "asynctasq"]


@overload
def get_setting(class_name: Literal["db"]) -> DBSettings: ...
@overload
def get_setting(class_name: Literal["http"]) -> HTTPSettings: ...
@overload
def get_setting(class_name: Literal["redis"]) -> RedisSettings: ...
@overload
def get_setting(class_name: Literal["app"]) -> AppSettings: ...
@overload
def get_setting(class_name: Literal["asynctasq"]) -> AsyncTasQSettings: ...
@overload
def get_setting(class_name: Literal["security"]) -> SecuritySettings: ...


def get_setting(
    class_name: SettingsName,
) -> (
    AppSettings
    | DBSettings
    | HTTPSettings
    | RedisSettings
    | SecuritySettings
    | AsyncTasQSettings
    | None
):
    """Returns the existing settings' class else None"""
    return {
        "db": DBSettings(),
        "http": HTTPSettings(),
        "app": AppSettings(),
        "redis": RedisSettings(),
        "security": SecuritySettings(),
        "asynctasq": AsyncTasQSettings(),
    }.get(class_name)
