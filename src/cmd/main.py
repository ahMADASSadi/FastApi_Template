import logging
from cmd.asynq import get_asynctasq_integration
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from api import v1_router
from config.openapi import custom_openapi
from config.settings import get_setting
from core.cache import Cache
from core.exception_handler import SecurityAwareExceptionHandler

# from core.key_manager import KeyManager
from core.limiter import limiter

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    app.state.limiter = limiter
    app.state.cache = Cache()
    # app.state.key_manager = KeyManager(cache=app.state.cache)
    try:
        async with get_asynctasq_integration().lifespan(app):
            yield
    finally:
        await app.state.cache.close()


def get_app() -> FastAPI:
    __settings = get_setting("app")

    title, debug = __settings.APP_NAME, __settings.DEBUG
    app = FastAPI(
        title=title,
        debug=debug,
        root_path="/api",
        lifespan=lifespan,
        docs_url="/v1/docs" if debug else None,
        redoc_url="/v1/redoc" if debug else None,
    )
    __security_settings = get_setting("security")
    if not debug:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=__security_settings.ALLOWED_ORIGINS,
            allow_methods=__security_settings.ALLOWED_METHODS,
            allow_credentials=True,
            allow_headers=__security_settings.ALLOWED_HEADERS,
        )
        app.add_middleware(HTTPSRedirectMiddleware)
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=[__security_settings.ALLOWED_HOSTS],  # type: ignore
        )
    app.add_middleware(SlowAPIMiddleware)

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> Response:
        return _rate_limit_exceeded_handler(request, exc)

    @app.exception_handler(401)
    async def api_exception_handler(request: Request, exc: Any) -> JSONResponse:
        return SecurityAwareExceptionHandler.handle_auth_error(request, exc, status_code=401)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return SecurityAwareExceptionHandler.handle_validation_error(request, exc)

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
        return SecurityAwareExceptionHandler.handle_not_found_error(request, exc)

    @app.exception_handler(Exception)
    async def internal_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return SecurityAwareExceptionHandler.handle_internal_error(request, exc, status_code=500)

    app.include_router(v1_router)
    app.openapi = lambda: custom_openapi(app, __settings.OPENAPI)
    add_pagination(app)
    return app


app: FastAPI = get_app()
