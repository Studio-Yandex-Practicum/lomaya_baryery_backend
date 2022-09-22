from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, EmailStr, PositiveInt

from src.core.db.db import get_session
from src.core.db.models import UserTask

router = APIRouter()


class UserTaskRequestModel(BaseModel):
    shift_id: PositiveInt = Field(
        ...,
        title='ID смены'
    )
    day_number: int = Field(
        ...,
        title='Номер дня, 0-100',
        ge=0,
        le=100
    )


class ShiftResponseModel(BaseModel):
    id: int
    status: str
    started_at: datetime
    finished_at: datetime


class TasksResponseModel(BaseModel):
    id: int
    name: str
    surname: str
    task_id: int
    task_description: str
    task_url: str


@router.get("/new_and_under_review_tasks")
async def get_new_and_under_review_tasks(
        #usertasks: UserTaskRequestModel,
        session: AsyncSession = Depends(get_session)
):
    return {"new_and_under_review_tasks": "hello world!"}
    pass
