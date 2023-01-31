from fastapi import Depends

from src.core.db.models import Administrator
from src.core.db.repository import AdministratorRepository


class AdministratorService:
    def __init__(self, administrator_repository: AdministratorRepository = Depends()):
        self.__administrator_repository = administrator_repository

    async def get_administrators_filter_by_role_and_status(
        self,
        status: Administrator.Status,
        role: Administrator.Role,
    ) -> list[Administrator]:
        """Получает список администраторов, опционально отфильтрованых по роли и/или статусу."""
        return await self.__administrator_repository.get_administrators_filter_by_role_and_status(status, role)
