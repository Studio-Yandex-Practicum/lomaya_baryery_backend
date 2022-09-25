from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Shift, User, Task, UserTask
from src.api.request_models.user_task import UserTaskRequestModel
from src.api.response_models.user_task import UserTasksResponseModel

router = APIRouter()


@router.post("/new_and_under_review_tasks")
async def get_new_and_under_review_tasks(
        usertask: UserTaskRequestModel,
        session: AsyncSession = Depends(get_session)
):
    usertask_data = usertask.dict()
    shift_id, day_number = usertask_data.values()
    get_info = await session.execute(
        select([
            ((Shift).where(Shift.id == shift_id)).label('shift'),

        ]

        )
    )
    return {shift_id: day_number}
