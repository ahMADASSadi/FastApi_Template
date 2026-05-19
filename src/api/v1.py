from fastapi.routing import APIRouter
from pydantic import BaseModel, Field

from services import echo_message_task

api_router = APIRouter(prefix="/v1")


class EchoTaskRequest(BaseModel):
    message: str = Field(min_length=1, max_length=512)


@api_router.post("/tasks/echo", status_code=202)
async def enqueue_echo_task(payload: EchoTaskRequest) -> dict[str, str]:
    task_id = await echo_message_task(message=payload.message).dispatch()
    return {
        "task_id": task_id,
        "queue": "default",
        "status": "queued",
    }
