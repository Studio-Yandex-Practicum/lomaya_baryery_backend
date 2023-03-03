from fastapi import File, UploadFile
from pydantic import Field

from src.api.request_models.request_base import RequestBase


class TaskRequest(RequestBase):
    description: str = Field(..., min_length=3, max_length=150)
    description_for_message: str = Field(..., min_length=3, max_length=150)


class TaskCreateRequest(TaskRequest):
    image: UploadFile = File(...)


class TaskUpdateRequest(TaskRequest):
    url: str
