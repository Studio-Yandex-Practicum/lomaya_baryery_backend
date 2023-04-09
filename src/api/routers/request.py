from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Body, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi_restful.cbv import cbv
from pydantic.schema import UUID

from src.api.request_models.request import RequestDeclineRequest
from src.api.response_models.error import generate_error_responses
from src.api.response_models.request import RequestResponse
from src.core.db import DTO_models, models
from src.core.services.authentication_service import AuthenticationService
from src.core.services.request_service import RequestService

router = APIRouter(prefix="/requests", tags=["Request"])


@cbv(router)
class RequestCBV:
    request_service: RequestService = Depends()
    authentication_service: AuthenticationService = Depends()
    token: HTTPAuthorizationCredentials = Depends(HTTPBearer())

    @router.patch(
        "/{request_id}/approve",
        response_model=RequestResponse,
        status_code=HTTPStatus.OK,
        summary="Одобрить заявку на участие.",
        responses=generate_error_responses(HTTPStatus.BAD_REQUEST, HTTPStatus.FORBIDDEN, HTTPStatus.NOT_FOUND),
    )
    async def approve_request_status(
        self,
        request_id: UUID,
        request: Request,
    ) -> RequestResponse:
        """Одобрить заявку на участие в акции."""
        await self.authentication_service.get_current_active_administrator(self.token.credentials)
        return await self.request_service.approve_request(request_id, request.app.state.bot_instance)

    @router.patch(
        "/{request_id}/decline",
        response_model=RequestResponse,
        status_code=HTTPStatus.OK,
        summary="Отклонить заявку на участие.",
        responses=generate_error_responses(HTTPStatus.BAD_REQUEST, HTTPStatus.FORBIDDEN, HTTPStatus.NOT_FOUND),
    )
    async def decline_request_status(
        self,
        request_id: UUID,
        request: Request,
        decline_request_data: RequestDeclineRequest | None = Body(None),
    ) -> RequestResponse:
        """Отклонить заявку на участие в акции."""
        await self.authentication_service.get_current_active_administrator(self.token.credentials)
        return await self.request_service.decline_request(
            request_id, request.app.state.bot_instance, decline_request_data
        )

    @router.get(
        "/",
        response_model=list[RequestResponse],
        status_code=HTTPStatus.OK,
        summary="Получить список заявок на участие.",
        response_description="Список заявок участников с фильтрацией по статусу заявки.",
    )
    async def get_requests_list(self, status: Optional[models.Request.Status] = None) -> list[DTO_models.RequestDTO]:
        """Получить список заявок с фильтрацией по статусу заявки.

        - **request_id**: id заявки
        - **user_id**: id участника
        - **name**: имя участника
        - **surname**: фамилия участника
        - **date_of_birth**: дата рождения участника
        - **city**: город участника
        - **phone_number**: номер телефона участника
        - **request_status**: статус заявки
        - **user_status**: статус участника
        """
        await self.authentication_service.get_current_active_administrator(self.token.credentials)
        return await self.request_service.get_requests_list(status)
