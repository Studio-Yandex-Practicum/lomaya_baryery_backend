from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from fastapi_restful.cbv import cbv

from src.core.services.registration_service import RegistrationService

router = APIRouter(tags=["Registration"])


@cbv(router)
class RegistrationCBV:
    registration_service: RegistrationService = Depends()

    @router.get(
        "/registration_template",
        response_class=HTMLResponse,
        summary="Запросить шаблон регистрации.",
    )
    async def get_registation_template(self) -> HTMLResponse:
        """Возвращает HTML шаблон для регистрации в telegram боте."""
        return await self.registration_service.get_template()
