import datetime as dt

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.api.request_models.administrator import AdministratorAuthenticateRequest
from src.api.response_models.administrator import TokenResponse
from src.core.db.models import Administrator
from src.core.db.repository import AdministratorRepository
from src.core.exceptions import (
    AdministratorBlockedException,
    InvalidAuthenticationDataException,
    UnauthorizedException,
)
from src.core.settings import settings

PASSWORD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="/administrators/login", scheme_name="JWT")

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

    async def get_administrator_by_email(self, email: str) -> Administrator:
        """Получить администратора по его email."""
        return await self.__administrator_repository.get_by_email_or_none(email)

    async def __authenticate_administrator(self, auth_data: AdministratorAuthenticateRequest) -> Administrator:
        """Аутентификация администратора по email и паролю."""
        administrator = await self.get_administrator_by_email(auth_data.email)
        if not administrator:
            raise InvalidAuthenticationDataException()
        if administrator.status == Administrator.Status.BLOCKED:
            raise AdministratorBlockedException()
        password = auth_data.password.get_secret_value()
        if not self.__verify_hashed_password(password, administrator.hashed_password):
            raise InvalidAuthenticationDataException()
        return administrator

    async def get_access_and_refresh_tokens(self, auth_data: AdministratorAuthenticateRequest) -> TokenResponse:
        """Получить access и refresh токены."""
        administrator = await self.__authenticate_administrator(auth_data)
        administrator.last_logined_at = dt.datetime.now()
        await self.__administrator_repository.update(administrator.id, administrator)

        subject = administrator.email
        tokens = {
            "access_token": self.__create_jwt_token(subject, ACCESS_TOKEN_EXPIRE_MINUTES),
            "refresh_token": self.__create_jwt_token(subject, REFRESH_TOKEN_EXPIRE_MINUTES),
        }
        return TokenResponse(**tokens)


async def get_current_active_administrator(
    token: str = Depends(OAUTH2_SCHEME), administrator_service: AdministratorService = Depends()
) -> Administrator:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise UnauthorizedException()
    except JWTError:
        raise UnauthorizedException()
    administrator = await administrator_service.get_administrator_by_email(email)
    if not administrator:
        raise UnauthorizedException()
    if administrator.status == Administrator.Status.BLOCKED:
        raise UnauthorizedException()
    return administrator
