# @app.middleware("http")
# async def log_request(
#     request: Request, call_next: Callable[[Request], Awaitable[Response]]
# ) -> Response:
#     logger.bind(context="FastAPI").info(
#         f"{request.method} {request.url.path}",
#         method=request.method,
#         path=request.url.path,
#         client=request.client.host if request.client else None,
#     )
#     response = await call_next(request)
#     logger.info(
#         f"Response {response.status_code}",
#         status_code=response.status_code,
#     )

#     return response
