from typing import Any


def has_permission(user: Any, permission: str,) -> bool:
    if not user:
        return False
    perms = getattr(user, "permissions", None)
    if perms is None:
        return False
    try:
        return permission in perms
    except TypeError:
        return False
