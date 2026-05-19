from typing import Any

from loguru import logger


class Logger:
    def __init__(self, context: str | None, *args, **kwargs):
        self.__logger = logger.bind(context=context)

    def info(self, message, attrs: dict[str, Any] | None = None):
        self.__logger.info(message, attrs)

    def debug(self, message, attrs: dict[str, Any] | None):
        self.__logger.debug(message, attrs)

    def warn(self, message, attrs: dict[str, Any] | None):
        self.__logger.warning(message, attrs)

    def error(self, message, trace, attrs: dict[str, Any] | None):
        self.__logger.error(message, attrs, trace)
