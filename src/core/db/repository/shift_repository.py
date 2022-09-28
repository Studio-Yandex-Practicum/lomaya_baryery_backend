from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.request_models.shift import ShiftCreateRequest
from src.core.db.models import Shift
from src.core.db.repository import AbstractRepository


class ShiftRepository(AbstractRepository):
    """Репозиторий для работы с моделью Shift."""

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.model = Shift

    async def get(self, obj_id: UUID) -> Shift:
        return await super().get(obj_id)

    async def create(self, obj_data: ShiftCreateRequest) -> Shift:
        return await super().create(obj_data)

    async def update(self):
        raise NotImplementedError(f"Метод `update` не определен в репозитории {self.__class__.__name__}")
