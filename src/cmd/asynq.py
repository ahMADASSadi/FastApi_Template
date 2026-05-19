from functools import lru_cache

from asynctasq import AsyncTasQIntegration, init

from config.settings import get_setting


def _setup_asynctasq() -> AsyncTasQIntegration:
    asynctasq_settings = get_setting("asynctasq")
    init(
        {
            "driver": asynctasq_settings.ASYNCTASQ_DRIVER,
            f"{asynctasq_settings.ASYNCTASQ_BROKER_URL}": {
                "url": str(asynctasq_settings.ASYNCTASQ_BROKER_URL),
            },
        }
    )
    return AsyncTasQIntegration()


@lru_cache(maxsize=1)
def get_asynctasq_integration() -> AsyncTasQIntegration:
    return _setup_asynctasq()
