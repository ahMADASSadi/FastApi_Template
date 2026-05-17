from redis.asyncio.client import Redis

from config.settings import RedisSettings, get_setting


class Cache:
    def __init__(
        self,
        settings: RedisSettings,
    ):
        host, port, password = (
            settings.REDIS_DSN.host,
            settings.REDIS_DSN.port,
            settings.REDIS_DSN.password,
        )
        self._redis = Redis(
            host=host,
            port=port or 6379,
            db=0,
            password=password,
        )


def get_cache() -> Cache:
    """Returns a singleton instance of the Cache class."""
    settings = get_setting("redis")
    return Cache(settings=settings)
