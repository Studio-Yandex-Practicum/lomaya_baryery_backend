from typing import Union
from uuid import UUID

from fastapi import APIRouter, Depends, Path, HTTPException

from src.api.response_models.user_task import UserTaskDB, UserTaskResponseModel
from src.core.services.shift_service import ShiftService, get_shift_service
from src.core.services.user_task_service import UserTaskService, get_user_task_service
from src.core.settings import settings

router = APIRouter()


@router.get(
    "/user/task/{shift_id}/{day_number}/new",
    response_model=UserTaskResponseModel,
    summary="Получить непроверенные и новые задания.",
)
async def get_new_and_under_review_tasks(
    shift_id: UUID = Path(..., title="ID смены"),
    day_number: int = Path(..., title="Номер дня, от 1 до 93", ge=settings.MIN_DAYS, le=settings.MAX_DAYS),
    user_task_service: UserTaskService = Depends(get_user_task_service),
    shift_service: ShiftService = Depends(get_shift_service)
) -> dict[str, Union[dict, list]]:
    """Получить непроверенные и новые задания.

    Запрос информации о непроверенных и новых
    заданиях участников по состоянию на указанный день
    в определенной смене:

    - **shift_id**: уникальный id смены, ожидается в формате UUID.uuid4
    - **day_number**: номер дня смены, в диапазоне от 1 до 93
    """
    shift = await shift_service.get_shift(shift_id)
    tasks = await user_task_service.get_tasks_report(shift_id, day_number)
    report = dict()
    report['shift'] = shift
    report['tasks'] = tasks
    return report


@router.get(
    "/user/task/{user_task_id}",
    response_model=UserTaskDB,
    response_model_exclude_none=True,
    summary="Получить информацию об отчёте участника.",
    response_description="Полная информация об отчёте участника.",
)
async def get_users_report(user_task_id: UUID, user_task_service: UserTaskService = Depends(get_user_task_service)):
    """Вернуть отчет участника.

    - **user_task_id**: номер задачи, назначенной участнику на день смены (генерируется рандомно при старте смены)
    - **task_id**: номер задачи
    - **day_number**: номер дня смены
    - **status**: статус задачи
    - **photo_url**: url фото выполненной задачи
    """
    user_task = await user_task_service.get(user_task_id=user_task_id)
    if user_task is None:
        raise HTTPException(status_code=404, detail="Задачи с указанным id не существует!")
    return user_task
