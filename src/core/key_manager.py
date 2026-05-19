# import httpx

# from config.settings import get_setting
# from core.cache import Cache


# class KeyManager:
#     """Manages JWT public key fetching and caching from the issuing service."""

#     CACHE_KEY = "jwt:public_key"
#     DEFAULT_TTL = 86400  # 24 hours

#     def __init__(self, cache: Cache, ttl: int = DEFAULT_TTL):
#         self.cache = cache
#         self.ttl = ttl
#         settings = get_setting("X")
#         self.issuer_url = settings.X_API_URL
#         self.key_url = settings.JWT_PUBLIC_KEY_URL + "/"
#         self.api_key = settings.API_KEY
#         self.api_secret = settings.API_SECRET
#         del settings  # Clean up reference to settings

#     async def get_public_key(self) -> str:
#         """
#         Retrieve the public key from cache or fetch from issuing service.
#         Falls back to cache on fetch failure to maintain availability.
#         """
#         cached_key = await self.cache.get(self.CACHE_KEY)
#         if cached_key:
#             return cached_key.decode("utf-8") if isinstance(cached_key, bytes) else cached_key

#         try:
#             key = await self._fetch_key_from_issuer()
#             await self.cache.set(self.CACHE_KEY, key, ttl=self.ttl)
#             return key
#         except Exception as e:
#             stale_key = await self.cache.get(self.CACHE_KEY)
#             if stale_key:
#                 return stale_key.decode("utf-8") if isinstance(stale_key, bytes) else stale_key
#             raise RuntimeError(
#                 f"Failed to fetch public key from {self.issuer_url}: {str(e)}"
#             ) from e

#     async def _fetch_key_from_issuer(self) -> str:
#         """Fetch the current public key from the issuing service's public key endpoint."""
#         timeout = httpx.Timeout(10.0, connect=5.0)

#         async with httpx.AsyncClient(timeout=timeout) as client:
#             response = await client.post(
#                 self.key_url,
#                 auth=httpx.BasicAuth(
#                     username=self.api_key,
#                     password=self.api_secret,
#                 ),
#             )
#             response.raise_for_status()
#             if public_key := response.json().get("public_key"):
#                 return public_key

#             raise ValueError(f"Invalid response from {self.key_url}: missing 'public_key' field")

#     async def refresh_key(self) -> str:
#         """Explicitly refresh the key by clearing cache and fetching new one."""
#         await self.cache.delete(self.CACHE_KEY)
#         return await self.get_public_key()
