from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import and_, not_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import exceptions
from src.core.db.db import get_session
from src.core.db.models import Administrator, AdministratorInvitation
from src.core.db.repository import AbstractRepository


class AdministratorInvitationRepository(AbstractRepository):
    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        super().__init__(session, AdministratorInvitation)

    async def get_mail_request_by_token(self, token: UUID) -> Optional[AdministratorInvitation]:
        statement = select(AdministratorInvitation).where(
            and_(
                AdministratorInvitation.token == token,
                AdministratorInvitation.expired_datetime > datetime.now(),
            )
        )
        result = (await self._session.scalars(statement)).first()
        if result is None:
            raise exceptions.AdministratorInvitationInvalidError
        return result

    async def get_all_invitations(self):
        """Возвращает из БД список приглашений, email которых не состоят в списке администраторов."""
        statement = select(AdministratorInvitation).where(
            not_(AdministratorInvitation.email.in_(select(Administrator.email)))
        )
        return (await self._session.scalars(statement)).all()
