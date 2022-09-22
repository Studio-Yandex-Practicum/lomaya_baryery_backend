from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
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
    return {shift_id: day_number}
