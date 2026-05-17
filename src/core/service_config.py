from dataclasses import dataclass

from fastapi import Depends

from core.cache import Cache, get_cache


@dataclass(frozen=True)
class BaseServiceConfig:
    cache_key_prefix: str
    logger: type
    cache: Cache = Depends(get_cache)
