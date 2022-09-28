from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.request_models.request import RequestRequest
from src.core.db.models import Request
from src.core.db.repository import AbstractRepository


class RequestRepository(AbstractRepository):
    """Репозиторий для работы с моделью Request."""

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.model = Request

    async def get(self, obj_id: UUID) -> Request:
        return await super().get(obj_id)

    async def create(self, obj_data: RequestRequest) -> Request:
        return await super().create(obj_data)

    async def update(self):
        raise NotImplementedError(f"Метод `update` не определен в репозитории {self.__class__.__name__}")
