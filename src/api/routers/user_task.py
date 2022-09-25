from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.request_models.user_task import UserTaskRequestModel
from src.api.response_models.user_task import UserTaskResponseModel
from src.core.db.db import get_session
from src.core.services.user_task_service import get_summary_user_tasks_response

router = APIRouter()


@router.post("/new_and_under_review_tasks", response_model=UserTaskResponseModel)
async def get_new_and_under_review_tasks(
        usertask: UserTaskRequestModel,
        session: AsyncSession = Depends(get_session)
):
    shift_id = usertask.shift_id
    day_number = usertask.day_number
    response = await get_summary_user_tasks_response(
        shift_id,
        day_number,
        session
    )
    return response
