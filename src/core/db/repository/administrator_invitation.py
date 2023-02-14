from datetime import datetime
from typing import Optional

from fastapi import Depends
from sqlalchemy import Text, and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Administrator, AdministratorInvitation
from src.core.db.repository import AbstractRepository
from src.core.exceptions import AdministratorInvitationInvalid


class AdministratorInvitationRepository(AbstractRepository):
    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        super().__init__(session, AdministratorInvitation)

    async def get_mail_request_by_token(self, token: str) -> Optional[AdministratorInvitation]:
        statement = select(AdministratorInvitation).where(
            and_(AdministratorInvitation.token == token, AdministratorInvitation.expired_date > datetime.utcnow())
        )
        result = (await self._session.scalars(statement)).first()
        if result is None:
            raise AdministratorInvitationInvalid
        return result

    async def get_invitaions(self) -> list[AdministratorInvitation]:

        result_statement = (
            select(
                func.coalesce(Administrator.name, AdministratorInvitation.name).label('name'),
                func.coalesce(Administrator.surname, AdministratorInvitation.surname).label('surname'),
                func.coalesce(Administrator.email, AdministratorInvitation.email).label('email'),
                func.coalesce(Administrator.role.cast(Text), Administrator.Role.PSYCHOLOGIST).label('role'),
            )
            .select_from(AdministratorInvitation)
            .join(
                Administrator,
                Administrator.email == AdministratorInvitation.email,
                isouter=True,
            )
        )

        invitations = await self._session.execute(result_statement)
        return invitations.all()
