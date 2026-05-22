import json
from typing import Any
from uuid import uuid4

from pydantic import TypeAdapter
from redis.asyncio.client import Redis
from redis.asyncio.connection import ConnectionPool
from redis.typing import DecodedT, EncodableT, ResponseT

from config.settings import get_setting


class Cache:
    def __init__(self, *args, **kwargs):
        __settings = get_setting("redis")
        host, port, password = (
            __settings.REDIS_DSN.host,
            __settings.REDIS_DSN.port,
            __settings.REDIS_DSN.password,
        )

        self._pool = ConnectionPool(
            host=host,
            port=port or 6379,
            db=0,
            password=password,
            max_connections=20,
        )
        self._redis = Redis(connection_pool=self._pool)

    async def close(self):
        """Close the redis client and disconnect the connection pool."""
        try:
            await self._redis.close()
        finally:
            await self._pool.disconnect()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def set(
        self, key: str, value: str | bytes | int | float | bool | EncodableT, ttl: int = 3600
    ) -> ResponseT:
        """Set a value with TTL (seconds)."""
        return await self._redis.set(key, value, ex=ttl)

    async def get(self, key: str) -> DecodedT:
        return await self._redis.get(key)

    async def delete(self, key: str) -> ResponseT:
        return await self._redis.delete(key)


class CacheHelper:
    """Generic caching helper for API endpoints with namespace-based invalidation."""

    def __init__(
        self, cache: Cache, namespace: str, ttl: int = 3600, version_ttl: int = 60 * 60 * 24 * 30
    ):
        """
        Initialize the cache helper.

        Args:
            cache: The Cache instance to use.
            namespace: A unique namespace identifier (e.g., "community_qa", "users").
            ttl: Default TTL in seconds for cached responses.
            version_ttl: TTL in seconds for the cache version key.
        """
        self.cache = cache
        self.namespace = namespace
        self.ttl = ttl
        self.version_ttl = version_ttl
        self._version_key = f":{namespace}:cache:version"

    @staticmethod
    def _normalize_payload(payload: Any) -> str:
        """Normalize cached payload to string."""
        if isinstance(payload, (bytes, bytearray)):
            return payload.decode("utf-8")
        return str(payload)

    async def get_version(self) -> str:
        """Get or create the current cache version for this namespace."""
        current_version = await self.cache.get(self._version_key)
        if current_version:
            return self._normalize_payload(current_version)

        version = str(uuid4())
        await self.cache.set(self._version_key, version, ttl=self.version_ttl)
        return version

    async def build_cache_key(
        self,
        scope: str,
        path: str,
        query_params: str,
        user_id: int | None = None,
    ) -> str:
        """
        Build a cache key with the namespace version, scope, path, query params, and optional user ID.

        Args:
            scope: Endpoint operation name (e.g., "list_questions", "retrieve_answer").
            path: Request path (e.g., "/community/questions").
            query_params: Stringified query parameters.
            user_id: Optional user ID for user-scoped caching.

        Returns:
            A formatted cache key string.
        """
        version = await self.get_version()
        user_scope = f":user:{user_id}" if user_id is not None else ""
        return f":{self.namespace}:{version}:{scope}:{path}:{query_params}{user_scope}"

    async def get_cached_response(self, cache_key: str, response_type: Any) -> Any | None:
        """
        Retrieve and deserialize a cached response.

        Args:
            cache_key: The cache key.
            response_type: The Pydantic response model type, or dict/list for raw data.

        Returns:
            The deserialized response or None if not cached.
        """
        payload = await self.cache.get(cache_key)
        if payload is None:
            return None

        normalized = self._normalize_payload(payload)
        data = json.loads(normalized)

        # If response_type is dict, list, or other built-in types, just parse and return
        if response_type in (dict, list) or not hasattr(response_type, "model_validate"):
            return data

        # Otherwise, validate as Pydantic model
        try:
            adapter = TypeAdapter(response_type)
            return adapter.validate_json(normalized, by_alias=True, by_name=True)
        except Exception:
            try:
                return TypeAdapter(response_type).validate_python(
                    data,
                    by_alias=True,
                    by_name=True,
                )
            except Exception:
                # Log the error and return None if deserialization fails
                return None

    async def set_cached_response(
        self,
        cache_key: str,
        response: Any,
        ttl: int | None = None,
        is_json: bool = False,
    ) -> None:
        """
        Serialize and cache a response.

        Args:
            cache_key: The cache key.
            response: The Pydantic model instance, dict, list, or JSON string to cache.
            ttl: Optional override for TTL (uses instance default if None).
            is_json: Whether the response is raw JSON data (dict/list) or already a JSON string.
        """

        if is_json:
            # Response is raw data (dict/list) or already a JSON string
            if isinstance(response, str):
                # Already a JSON string
                value = response
            else:
                value = json.dumps(response)
        else:
            value = response.model_dump_json(
                by_alias=True, exclude_none=False, exclude={"exclusion_fields"}
            )

        await self.cache.set(
            cache_key,
            value,
            ttl=ttl or self.ttl,
        )

    async def invalidate(self) -> None:
        """Invalidate all cached responses in this namespace by rotating the version key."""
        await self.cache.set(
            self._version_key,
            str(uuid4()),
            ttl=self.version_ttl,
        )
