from fastapi import HTTPException


async def check_user_task_exists(user_task):
    """Проверить наличие отчета участника в БД по id."""
    if user_task is None:
        raise HTTPException(status_code=404, detail="Задачи с указанным id не существует!")
