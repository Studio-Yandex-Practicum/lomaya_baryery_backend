from fastapi import APIRouter, Depends
from fastapi_restful.cbv import cbv

from src.api.request_models.administrator import AdministratorCreateRequest
from src.core.services.administrator_service import AdministratorService

router = APIRouter(prefix="/administrators", tags=["Administrator"])


@cbv(router)
class AdministratorCBV:
    administrator_service: AdministratorService = Depends()

    @router.post("/")
    async def create_new_administrator(
        self,
        administrator: AdministratorCreateRequest,
    ):  # TODO: response
        return await self.administrator_service.create_new_administrator(administrator)
