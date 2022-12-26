import datetime as dt
from typing import Optional

from fastapi import Depends
from jose import jwt
from passlib.context import CryptContext

from src.api.request_models.administrator import (
    AdministratorAuthenticateRequest,
    AdministratorCreateRequest,
)
from src.api.response_models.administrator import TokenResponse
from src.core.db.models import Administrator
from src.core.db.repository import AdministratorRepository
from src.core.exceptions import (
    AdministratorAlreadyExistException,
    InvalidCredentialsException,
)
from src.core.settings import settings

PASSWORD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 10
ALGORITHM = "HS256"


class AdministratorService:
    def __init__(self, administrator_repository: AdministratorRepository = Depends()):
        self.__administrator_repository = administrator_repository

    def __get_hashed_password(self, password: str) -> str:
        """Получить хэш пароля."""
        return PASSWORD_CONTEXT.hash(password)

    def __verify_hashed_password(self, plain_password: str, hashed_password: str) -> bool:
        """Сравнить открытый пароль с хэшем."""
        return PASSWORD_CONTEXT.verify(plain_password, hashed_password)

    def __create_jwt_token(self, subject: str, expires_delta: int) -> str:
        """Создать jwt-токен.

        Аргументы:
            subject (str) - субьект токена
            expires_delta (int) - время жизни токена
        """
        expire = dt.datetime.utcnow() + dt.timedelta(minutes=expires_delta)
        to_encode = {"sub": subject, "exp": expire}
        return jwt.encode(to_encode, settings.SECRET_KEY, ALGORITHM)

    async def __authenticate_administrator(self, auth_data: AdministratorAuthenticateRequest) -> Administrator:
        """Аутентификация администратора по email и паролю."""
        administrator = await self.__administrator_repository.get_by_email_or_none(auth_data.email)
        if not administrator:
            raise InvalidCredentialsException()
        password = auth_data.password.get_secret_value()
        if not self.__verify_hashed_password(password, administrator.hashed_password):
            raise InvalidCredentialsException()
        return administrator

    async def get_access_and_refresh_tokens(self, auth_data: AdministratorAuthenticateRequest) -> TokenResponse:
        """Получить access и refresh токены."""
        administrator = await self.__authenticate_administrator(auth_data)
        administrator.last_logined_at = dt.datetime.now()
        await self.__administrator_repository.update(administrator.id, administrator)

        subject = administrator.__repr__()
        tokens = {
            "access_token": self.__create_jwt_token(subject, ACCESS_TOKEN_EXPIRE_MINUTES),
            "refresh_token": self.__create_jwt_token(subject, REFRESH_TOKEN_EXPIRE_MINUTES),
        }
        return TokenResponse(**tokens)

    async def create_new_administrator(
        self,
        new_administrator: AdministratorCreateRequest,
        role: Optional[Administrator.Role] = Administrator.Role.PSYCHOLOGIST,
        status: Optional[Administrator.Status] = Administrator.Status.ACTIVE,
    ) -> Administrator:
        """Создать администратора.

        Аргументы:
            role (опционально, Administrator.Role) - роль администратора (администратор, психолог)
            status (опционально, Administrator.Status) - статус администратора (активен, заблокирован)
        """
        if await self.__administrator_repository.get_by_email_or_none(new_administrator.email):
            raise AdministratorAlreadyExistException()
        password = new_administrator.password.get_secret_value()
        new_administrator = new_administrator.dict(exclude={'password'})
        new_administrator["hashed_password"] = self.__get_hashed_password(password)
        new_administrator["role"] = role
        new_administrator["status"] = status
        return await self.__administrator_repository.create(Administrator(**new_administrator))
