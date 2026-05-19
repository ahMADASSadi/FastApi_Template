from dataclasses import dataclass, field

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)


@dataclass
class LimiteRate:
    items: dict[str, str] = field(default_factory=dict)

    @classmethod
    def get_rate(cls, endpoint: str) -> str:

        return {}.get(endpoint, "100/minute")
