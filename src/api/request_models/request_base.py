from pydantic import BaseModel, Extra


class RequestBase(BaseModel):
    """Базовый класс для моделей запросов.

    Запрещена передача полей не предусмотренных схемой."""

    class Config:
        extra = Extra.forbid
