from sqlalchemy import select, asc
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union

from src.core.crud.base import CRUDBase
from src.core.db.models import Request


class CRUDRequest(CRUDBase):
    async def get_by_attribute_latest(self, attr_name: str,
                                      attr_value: Union[str, bool],
                                      session: AsyncSession, ):
        attr = getattr(self.model, attr_name)
        db_obj = await session.execute(
            select(self.model).where(attr == attr_value).order_by(
                asc(self.model.created_date)
            )
        )
        return db_obj.scalars().first()


request_crud = CRUDRequest(Request)
