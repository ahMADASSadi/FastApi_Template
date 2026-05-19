# import logging

# import jwt
# from fastapi import Depends, Header, HTTPException, Request, status

# from config.settings import get_setting

# logger = logging.getLogger(__name__)


# async def __get_current_user(
#     request: Request,
#     user_repo: UserRepository = Depends(get_user_repo),
#     authorization: str | None = Header(None, convert_underscores=False),
# ):
#     if not authorization:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header"
#         )

#     parts = authorization.split()
#     if len(parts) != 2 or parts[0].lower() != "bearer":
#         raise HTTPException(status_code=401, detail="Invalid Authorization header")

#     token = parts[1]
#     settings = get_setting("app")
#     key_manager = request.app.state.key_manager

#     # Attempt to validate with cached key
#     try:
#         public_key = await key_manager.get_public_key()
#         payload = jwt.decode(
#             token,
#             public_key,
#             algorithms=["RS256"],
#             audience=settings.AUDIENCE,
#             issuer=settings.ISSUER,
#         )
#         user = await user_repo.get(user_id=payload.get("user_id"))
#         if not user:
#             logger.warning(
#                 "User not found in database",
#                 extra={"user_id": payload.get("user_id"), "issuer": settings.ISSUER},
#             )
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
#         return user

#     except jwt.InvalidTokenError as e:
#         # Token validation failed; check if it's due to key mismatch by refreshing
#         logger.warning(
#             "Token validation failed with cached key",
#             extra={"exception_type": type(e).__name__, "will_retry": True},
#         )
#         try:
#             fresh_key = await key_manager.refresh_key()
#             payload = jwt.decode(
#                 token,
#                 fresh_key,
#                 algorithms=["RS256"],
#                 audience=settings.AUDIENCE,
#                 issuer=settings.ISSUER,
#             )
#             user = await user_repo.get(user_id=payload.get("user_id"))
#             if not user:
#                 logger.warning(
#                     "User not found in database after key refresh",
#                     extra={"user_id": payload.get("user_id")},
#                 )
#                 raise HTTPException(
#                     status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
#                 )
#             logger.info("Token validated after key refresh (issuer rotation detected)")
#             return user
#         except (jwt.InvalidTokenError, HTTPException):
#             # Token is truly invalid (not a key rotation issue)
#             logger.warning("Token validation failed after key refresh - token is invalid")
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
#             )
#         except Exception as exc:
#             # Unexpected error during retry
#             logger.error(
#                 "Unexpected error during token validation retry",
#                 extra={
#                     "exception_type": type(exc).__name__,
#                     "message": str(exc),
#                 },
#             )
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
#             )
#     except (ValueError, TypeError) as e:
#         logger.warning(
#             "Invalid token format",
#             extra={"exception_type": type(e).__name__},
#         )
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token format")
#     except Exception as e:
#         # Catch-all for unexpected errors (db, cache, network, etc.)
#         logger.error(
#             "Unexpected error during authentication",
#             extra={
#                 "exception_type": type(e).__name__,
#                 "message": str(e),
#             },
#         )
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
#         )


# async def get_current_user(
#     request: Request,
#     user_repo: UserRepository = Depends(get_user_repo),
#     authorization: str | None = Header(None, convert_underscores=False),
# ):
#     """Auth dependency: expects `Authorization` header containing a Bearer token.

#     Decodes the JWT token using the issuer's public key (fetched from X API and cached).
#     Automatically refreshes the key if validation fails to handle key rotation.
#     """
#     return await __get_current_user(
#         request=request, user_repo=user_repo, authorization=authorization
#     )


# async def get_current_user_optional(
#     request: Request,
#     user_repo: UserRepository = Depends(get_user_repo),
#     authorization: str | None = Header(None, convert_underscores=False),
# ):
#     """Optional auth dependency: returns authenticated user if valid `Authorization` header is provided, else None."""
#     if not authorization:
#         return None
#     try:
#         return await __get_current_user(
#             request=request, user_repo=user_repo, authorization=authorization
#         )
#     except HTTPException as exc:
#         if exc.status_code == status.HTTP_401_UNAUTHORIZED:
#             return None  # Treat invalid/missing token as unauthenticated (None)
#         raise  # Re-raise other exceptions (e.g. malformed token)
