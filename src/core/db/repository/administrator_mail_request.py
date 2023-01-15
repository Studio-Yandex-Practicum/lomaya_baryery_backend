from typing import Optional

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import AdministratorMailRequest
from src.core.db.repository import AbstractRepository


class AdministratorMailRequestRepository(AbstractRepository):
    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        super().__init__(session, AdministratorMailRequest)

    async def get_invite_by_token(self, token: str) -> Optional[AdministratorMailRequest]:
        statement = select(AdministratorMailRequest).where(AdministratorMailRequest.token == token)
        return (await self._session.scalars(statement)).first()
