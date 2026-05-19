from dataclasses import dataclass

from core.logger import Logger


@dataclass(frozen=True)
class BaseServiceConfig:
    cache_prefix: str
    cache_ttl: int
    logger: Logger
