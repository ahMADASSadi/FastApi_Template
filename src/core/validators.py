from functools import wraps
from re import Pattern, compile

PHONE_REGEX = compile(pattern=r"^(?:0|\+98)(9\d{9})$")


def validate_phone_with_pattern(phone: str, pattern: Pattern = PHONE_REGEX) -> str | None:
    """
    Normalize phone number to pattern format

    Examples:
        >>> validate_phone_with_pattern('+98 912 345 6789', r"^(?:09|\+98)(\d{9})$") -> '09123456789'
    """

    clean_phone = phone.replace(" ", "").replace("-", "")

    match = pattern.match(clean_phone)
    if match:
        return f"0{match.group(1)}"
    return None


def set_status_for_object_based_on_role(role: list[str] | str):
    def decorator(function):
        @wraps(function)
        async def wrapper(*args, **kwargs):
            request_user = kwargs.get("user")
            if request_user is None and len(args) > 1:
                request_user = args[1]

            result = await function(*args, **kwargs)

            request_role = getattr(request_user, "role", None)
            if request_role is None:
                roles = getattr(request_user, "user_roles", None) or []
                request_role = next(
                    (
                        getattr(item, "role", None) or getattr(item, "name", None)
                        for item in roles
                        if (getattr(item, "role", None) or getattr(item, "name", None))
                    ),
                    None,
                )

            status = 1 if request_role == role else 0

            if hasattr(result, "publish_status"):
                result.publish_status = status
                # await self.db.flush()

            return result

        return wrapper

    return decorator
