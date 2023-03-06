import logging
from typing import Optional, Any

from pydantic import BaseModel
from celery import Celery, states
from fastapi import FastAPI, APIRouter

from src.utils import get_app
from src.config import CONFIG


logger = logging.getLogger("api")

router = APIRouter()
app: FastAPI = get_app()
tasks = Celery(broker=CONFIG.BROKER_URL, backend=CONFIG.REDIS_URL)


class TaskResult(BaseModel):
    id: str
    status: str
    error: Optional[str] = None
    result: Optional[Any] = None


@app.get("/task/{task_id}", status_code=200)
def get_task_result(task_id: str):
    """
    Endpoint to check the status of a task.
    Args:
        task_id (str): Id of task.
    Return:
        JSONResponse: TaskResult in json format.
    """
    result = tasks.AsyncResult(task_id)

    output = TaskResult(
        id=task_id,
        status=result.state,
        error=str(result.info) if result.failed() else None,
        result=result.get() if result.state == states.SUCCESS else None,
    )

    return output.dict()
