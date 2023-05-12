import datetime as dt

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.api.request_models.administrator import AdministratorAuthenticateRequest
from src.core import exceptions
from src.core.db.DTO_models import AdministratorAndTokensDTO
from src.core.db.models import Administrator
from src.core.db.repository import AdministratorRepository
from src.core.settings import settings

PASSWORD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="/administrators/login", scheme_name="JWT")

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 10
ALGORITHM = "HS256"


class AuthenticationService:
    def __init__(self, administrator_repository: AdministratorRepository = Depends()):
        self.__administrator_repository = administrator_repository

    @staticmethod
    def get_hashed_password(password: str) -> str:
        """Получить хэш пароля."""
        return PASSWORD_CONTEXT.hash(password)

    @staticmethod
    def get_email_from_token(token: str) -> str:
        """Возвращает email из JWT токена."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            raise exceptions.UnauthorizedError
        email = payload.get("email")
        if not email:
            raise exceptions.UnauthorizedError
        return email

    def __verify_hashed_password(self, plain_password: str, hashed_password: str) -> bool:
        """Сравнить открытый пароль с хэшем."""
        return PASSWORD_CONTEXT.verify(plain_password, hashed_password)

    def __create_jwt_token(self, email: str, expires_delta: int) -> str:
        """Создать jwt-токен.

        Аргументы:
            email (str) - эл. почта пользователя
            expires_delta (int) - время жизни токена
        """
        expire = dt.datetime.utcnow() + dt.timedelta(minutes=expires_delta)
        to_encode = {"email": email, "exp": expire}
        return jwt.encode(to_encode, settings.SECRET_KEY, ALGORITHM)

    async def __authenticate_administrator(self, auth_data: AdministratorAuthenticateRequest) -> Administrator:
        """Аутентификация администратора по email и паролю."""
        administrator = await self.__administrator_repository.get_by_email(auth_data.email)
        if administrator.status == Administrator.Status.BLOCKED:
            raise exceptions.AdministratorBlockedError
        password = auth_data.password.get_secret_value()
        if not self.__verify_hashed_password(password, administrator.hashed_password):
            raise exceptions.InvalidAuthenticationDataError
        return administrator

    async def login(self, auth_data: AdministratorAuthenticateRequest) -> AdministratorAndTokensDTO:
        """Получить refresh- и access- токены и информацию об администраторе."""
        administrator = await self.__authenticate_administrator(auth_data)
        administrator.last_login_at = dt.datetime.now()
        await self.__administrator_repository.update(administrator.id, administrator)
        return AdministratorAndTokensDTO(
            access_token=self.__create_jwt_token(administrator.email, ACCESS_TOKEN_EXPIRE_MINUTES),
            refresh_token=self.__create_jwt_token(administrator.email, REFRESH_TOKEN_EXPIRE_MINUTES),
            administrator=administrator,
        )

    async def check_administrator_by_token(
        self,
        token: HTTPAuthorizationCredentials,
        role: Administrator.Role | None = None,
    ) -> None:
        """Проверяет существование администратора по token-у и его роли (опционально).

        Администратор должен существовать, иметь статус ACTIVE, а также
        иметь роль, указанную в аргументах.
        Если одно из условий не выполняется, выбрасывается исключение.
        Если role=None, то роль администратора не проверяется.

        Args:
            token (str): JWT token.
            role (Administrator.Role): роль администратора или None — тогда
                                       роль администратора не проверяется.
        """
        if role is not None and role not in Administrator.Role.__members__.values():
            raise exceptions.AdministratorUnknownRoleError(role)

        email = self.get_email_from_token(token.credentials)

        administrator_exists = await self.__administrator_repository.is_administrator_exists(email, role)

        if not administrator_exists:
            raise exceptions.ForbiddenError

    async def get_current_active_administrator(self, token: str) -> Administrator:
        """Получить текущего активного администратора, используя токен."""
        email = self.get_email_from_token(token)
        administrator = await self.__administrator_repository.get_by_email(email)
        if administrator.status == Administrator.Status.BLOCKED:
            raise exceptions.AdministratorBlockedError
        return administrator

    async def refresh(self, refresh_token: str | None) -> AdministratorAndTokensDTO:
        """Получить новую пару refresh- и access- токенов и информацию об администраторе."""
        if not refresh_token:
            raise exceptions.UnauthorizedError
        administrator = await self.get_current_active_administrator(refresh_token)
        return AdministratorAndTokensDTO(
            access_token=self.__create_jwt_token(administrator.email, ACCESS_TOKEN_EXPIRE_MINUTES),
            refresh_token=self.__create_jwt_token(administrator.email, REFRESH_TOKEN_EXPIRE_MINUTES),
            administrator=administrator,
        )
