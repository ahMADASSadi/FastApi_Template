# from typing import Any

# from fastapi import Depends, HTTPException, status

# from core.auth import get_current_user


# def require_permission(permission: str):
#     async def permission_check(current_user: Any = Depends(get_current_user)):
#         if not has_permission(current_user, permission):
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
#             )
#         return current_user

#     return permission_check


# def has_permission(user: Any, permission: str) -> bool:
#     # Safe check: user may be None or not have a permissions attribute
#     if not user:
#         return False
#     perms = getattr(user, "permissions", None)
#     if perms is None:
#         return False
#     try:
#         return permission in perms
#     except TypeError:
#         return False
