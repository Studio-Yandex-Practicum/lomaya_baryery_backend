from pydantic import BaseModel, Field, PositiveInt


class UserTaskRequestModel(BaseModel):
    """Модель для запроса списка непроверенных отчётов,
    принимает id смены и номер дня (от 1 до 100).
    """

    shift_id: PositiveInt = Field(
        ...,
        title='ID смены'
    )
    day_number: int = Field(
        ...,
        title='Номер дня, 1-100',
        ge=1,
        le=100
    )
