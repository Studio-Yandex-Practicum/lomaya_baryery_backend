from fastapi import Depends

from src.core.db.repository import AdministratorRepository


class AdministratorService:
    def __init__(self, administrator_repository: AdministratorRepository = Depends()):
        self.__administrator_repository = administrator_repository
