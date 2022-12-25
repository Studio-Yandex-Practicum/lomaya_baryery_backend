from typing import Optional

from fastapi import Depends
from passlib.context import CryptContext

from src.api.request_models.administrator import AdministratorCreateRequest
from src.core.db.models import Administrator
from src.core.db.repository import AdministratorRepository

PASSWORD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AdministratorService:
    def __init__(self, administrator_repository: AdministratorRepository = Depends()):
        self.__administrator_repository = administrator_repository

    def _get_hashed_password(self, password: str) -> str:
        """Получить хэш пароля."""
        return PASSWORD_CONTEXT.hash(password)

    def _verify_hashed_password(self, plain_password: str, hashed_password: str) -> bool:
        """Сравнить открытый пароль с хэшем."""
        return PASSWORD_CONTEXT.verify(plain_password, hashed_password)

    async def create_new_administrator(
        self,
        new_administrator: AdministratorCreateRequest,
        role: Optional[Administrator.Role] = Administrator.Role.PSYCHOLOGIST,
        status: Optional[Administrator.Status] = Administrator.Status.ACTIVE,
    ) -> Administrator:
        """Создать администратора."""
        # TODO: верификация, существует админ или нет?
        new_administrator = new_administrator.dict()
        password = new_administrator.pop("password")
        new_administrator["hashed_password"] = self._get_hashed_password(password)
        new_administrator["role"] = role
        new_administrator["status"] = status
        return await self.__administrator_repository.create(Administrator(**new_administrator))

    async def update_administrator(self):
        pass  # TODO
