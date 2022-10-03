from uuid import UUID

from fastapi import Depends

from src.api.request_models.shift import ShiftCreateRequest
from src.core.db.models import Shift
from src.core.db.repository import ShiftRepository


class ShiftService:
    def __init__(self, shift_repository: ShiftRepository = Depends()) -> None:
        self.shift_repository = shift_repository

    async def create_new_shift(self, new_shift: ShiftCreateRequest) -> Shift:
        shift = Shift(**new_shift.dict())
        shift.status = Shift.Status.PREPARING
        return await self.shift_repository.create(shift=shift)

    async def get_shift(self, id: UUID) -> Shift:
        return await self.shift_repository.get(id)

    async def update_shift(self, id: UUID, update_shift_data: ShiftCreateRequest) -> Shift:
        return await self.shift_repository.update(id=id, shift=Shift(**update_shift_data.dict()))
