from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.db.models import Request, User


class RequestService:

    async def list_all_requests(
        list_request,
        session: AsyncSession
    ):
        request_data = list_request.dict()
        if request_data["status"] != "all":
            db_list_request = await session.execute(
                select((Request.user_id).label("user_id"),
                       (Request.id).label("request_id"),
                       (Request.status).label("status"),
                       (User.name).label("name"),
                       (User.surname).label("surname"),
                       (User.date_of_birth).label("date_of_birth"),
                       (User.city).label("city"),
                       (User.phone_number).label("phone"),).join(
                        User).where(
                            and_(
                                Request.shift_id == request_data["shift_id"],
                                Request.status == request_data["status"]
                            )
                        )
                    )
        else:
            db_list_request = await session.execute(
                select((Request.user_id).label("user_id"),
                       (Request.id).label("request_id"),
                       (Request.status).label("status"),
                       (User.name).label("name"),
                       (User.surname).label("surname"),
                       (User.date_of_birth).label("date_of_birth"),
                       (User.city).label("city"),
                       (User.phone_number).label("phone"),
                       ).join(
                        User).where(
                            and_(
                                Request.shift_id == request_data["shift_id"],
                            )
                        )
                    )
        return db_list_request.all()
