from src.core.crud.base import CRUDBase
from src.core.db.models import User


class CRUDUser(CRUDBase):
    pass


user_crud = CRUDUser(User)
