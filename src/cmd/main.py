from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi_pagination import add_pagination

from api import v1
from config.settings import get_setting


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield


def get_app() -> FastAPI:
    __settings = get_setting("app")

    title, debug = __settings.APP_NAME, __settings.DEBUG
    app = FastAPI(
        title=title,
        debug=debug,
        root_path="/api",
        lifespan=lifespan,
        docs_url="/docs" if debug else None,
        redoc_url="/redoc" if debug else None,
    )

    # @app.exception_handler(404)
    # async def api_exception_handler(_: Request, exc: BaseException) -> JSONResponse:
    #     print(vars(exc))
    #     return JSONResponse(
    #         status_code=exc.status_code,
    #         content={
    #             "success": False,
    #             "message": exc.detail,  # type:ignore
    #             "data": exc.detail.get("data", None),
    #         },
    #     )

    app.include_router(v1)

    add_pagination(app)

    return app


app: FastAPI = get_app()
