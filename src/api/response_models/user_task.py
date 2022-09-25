from datetime import date
from typing import List

from pydantic import BaseModel, Field, Extra


class ShiftResponseModel(BaseModel):
    """Модель смены для ответа."""

    id: int
    status: str
    started_at: date
    finished_at: date

    class Config:
        orm_mode = True


# class UserInfoToTasksResponse(BaseModel):
#     name: str
#     surname: str
#
#     class Config:
#         extra = Extra.ignore
#         orm_mode = True


# class TaskInfoToTasksResponse(BaseModel):
#     description: str = Field(alias='task_description')
#     url: str = Field(alias='task_url')
#
#     class Config:
#         allow_population_by_field_name = True
#         extra = Extra.ignore
#         orm_mode = True


# class UserTaskInfoToTasksResponse(BaseModel):
#     id: int
#     task_id: int
#
#     class Config:
#         extra = Extra.ignore
#         orm_mode = True


# class TasksResponseModel(UserInfoToTasksResponse,
#                          UserTaskInfoToTasksResponse,
#                          TaskInfoToTasksResponse):
#     """Модель задания для ответа."""
#     pass


class TaskResponseModel(BaseModel):
    """Модель c информацией о задании и юзере для ответа."""

    id: int
    name: str
    surname: str
    task_id: int
    task_description: str
    task_url: str


class UserTasksResponseModel(BaseModel):
    """Общая модель смены и заданий для ответа."""
    shift: ShiftResponseModel
    tasks: List[TaskResponseModel]
