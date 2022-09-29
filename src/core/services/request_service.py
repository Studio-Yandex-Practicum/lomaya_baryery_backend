from fastapi import Depends
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.request_models.request import RequestList
from src.api.response_models.request import RequestDB
from src.core.db.db import get_session
from src.core.db.models import Request, User


class RequestService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all_requests(
        self,
        list_request: RequestList,
    ) -> list[RequestDB]:
        db_list_request = await self.session.execute(
            select((Request.user_id),
                   (Request.id).label("request_id"),
                   (Request.status),
                   (User.name),
                   (User.surname),
                   (User.date_of_birth),
                   (User.city),
                   (User.phone_number.label("phone"))).join(
                    User).where(
                        or_(Request.shift_id == list_request.shift_id),
                        or_(list_request.status is None,
                            Request.status == list_request.status)
                        )
                    )
        return db_list_request.all()


def get_request_service(session: AsyncSession = Depends(get_session)) -> RequestService:
    return RequestService(session)
