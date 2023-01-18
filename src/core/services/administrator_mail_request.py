import hashlib
import secrets

from fastapi import Depends

from src.api.request_models.administrator import AdministratorMailRequestRequest
from src.core.db.models import AdministratorMailRequest
from src.core.db.repository import AdministratorMailRequestRepository
from src.core.exceptions import AdministratorInviteForbidden


class AdministratorMailRequestService:
    def __init__(self, administrator_mail_request_repository: AdministratorMailRequestRepository = Depends()) -> None:
        self.__administrator_mail_request_repository = administrator_mail_request_repository

    async def create_mail_request(self, invitation_data: AdministratorMailRequestRequest) -> str:
        key = secrets.token_bytes()
        token = hashlib.sha256(key).hexdigest()
        new_invite = AdministratorMailRequest(**invitation_data.dict(), token=token)
        await self.__administrator_mail_request_repository.create(new_invite)
        return key.hex()

    async def get_active_mail_request(self, key: str) -> AdministratorMailRequest:
        token = hashlib.sha256(bytes.fromhex(key)).hexdigest()
        invite = await self.__administrator_mail_request_repository.get_mail_request_by_token(token)
        if not invite:
            raise AdministratorInviteForbidden
        return invite
