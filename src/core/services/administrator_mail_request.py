import hashlib
import secrets
from datetime import datetime
from typing import Optional

from fastapi import Depends

from src.api.request_models.administrator import AdministratorMailRequestRequest
from src.core.db.models import AdministratorMailRequest
from src.core.db.repository import AdministratorMailRequestRepository
from src.core.exceptions import AdministratorInviteForbidden


class AdministratorMailRequestService:
    def __init__(self, administrator_mail_request_repository: AdministratorMailRequestRepository = Depends()) -> None:
        self.__administrator_mail_request_repository = administrator_mail_request_repository

    async def create_invite(self, invitation_data: AdministratorMailRequestRequest) -> str:
        key = secrets.token_bytes()
        token = hashlib.sha256(key).hexdigest()
        new_invite = AdministratorMailRequest(**invitation_data.dict(), token=token)
        await self.__administrator_mail_request_repository.create(new_invite)
        return key.hex()

    async def get_invite_by_token(self, token: str) -> Optional[AdministratorMailRequest]:
        return await self.__administrator_mail_request_repository.get_invite_by_token(token)

    async def verify_token(self, token: str) -> AdministratorMailRequest:
        verification_key = hashlib.sha256(bytes.fromhex(token)).hexdigest()
        invite = await self.get_invite_by_token(verification_key)
        if not invite or datetime.utcnow() > invite.expired_date:
            raise AdministratorInviteForbidden
        return invite
