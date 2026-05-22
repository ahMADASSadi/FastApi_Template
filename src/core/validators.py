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
