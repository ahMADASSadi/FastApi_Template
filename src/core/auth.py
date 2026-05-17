from typing import Optional

import jwt
from fastapi import Depends, Header, HTTPException, status

from config.settings import get_setting


async def get_current_user(
    user_repo: type = Depends(),
    authorization: Optional[str] = Header(None, convert_underscores=False),
):
    """Auth dependency: expects `Authorization` header containing a Bearer token.

    Decodes the JWT token using DanaJouSettings shared secret key and returns the authenticated user.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authorization header format"
        )
    token = authorization.split(" ")[1]

    try:
        settings = get_setting("jwt")
        payload = jwt.decode(
            token,
            # settings.PUBLIC_KEY,
            algorithms=["RS256"],
            # audience=settings.AUDIENCE,
            issuer=settings.ISSUER,
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token format")

    user = await user_repo.get(user_id=payload.get("user_id"))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
