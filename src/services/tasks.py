from asynctasq import task


@task(queue="default")
async def echo_message_task(message: str) -> str:
    return f"processed: {message}"
