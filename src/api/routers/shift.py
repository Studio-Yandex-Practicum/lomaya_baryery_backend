from http import HTTPStatus
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page
from fastapi_restful.cbv import cbv

from src.api.request_models.paginate import PaginationRequest
from src.api.request_models.shift import ShiftCreateRequest
from src.api.response_models.shift import (
    ShiftDtoRespone,
    ShiftResponse,
    ShiftUsersResponse,
)
from src.core.db.models import Request
from src.core.services.shift_service import ShiftService

router = APIRouter(prefix="/shifts", tags=["Shift"])


STR_STATUS_DENIES_START_SHIFT = "Нельзя запустить уже начатую, отмененную или завершенную смену."


@cbv(router)
class ShiftCBV:
    shift_service: ShiftService = Depends()

    @router.post(
        "/",
        response_model=ShiftResponse,
        response_model_exclude_none=True,
        status_code=HTTPStatus.CREATED,
        summary="Создать новую смену",
        response_description="Информация о созданной смене",
    )
    async def create_new_shift(
        self,
        shift: ShiftCreateRequest,
    ) -> ShiftResponse:
        """Создать новую смену.

        - **started_at**: дата начала смены
        - **finished_at**: дата окончания смены
        """
        return await self.shift_service.create_new_shift(shift)

    @router.get(
        "/{shift_id}",
        response_model=ShiftResponse,
        response_model_exclude_none=True,
        status_code=HTTPStatus.OK,
        summary="Получить информацию о смене",
        response_description="Информация о смене",
    )
    async def get_shift(
        self,
        shift_id: UUID,
    ) -> ShiftResponse:
        """Получить информацию о смене по её ID.

        - **shift_id**: уникальный индентификатор смены
        - **status**: статус смены (started|finished|preparing|cancelled)
        - **started_at**: дата начала смены
        - **finished_at**: дата окончания смены
        """
        return await self.shift_service.get_shift(shift_id)

    @router.patch(
        "/{shift_id}",
        response_model=ShiftResponse,
        response_model_exclude_none=True,
        status_code=HTTPStatus.OK,
        summary="Обновить информацию о смене",
        response_description="Обновленная информация о смене",
    )
    async def update_shift(
        self,
        shift_id: UUID,
        update_shift_data: ShiftCreateRequest,
    ) -> ShiftResponse:
        """Обновить информацию о смене с указанным ID.

        - **shift_id**: уникальный индентификатор смены
        - **started_at**: дата начала смены
        - **finished_at**: дата окончания смены
        """
        return await self.shift_service.update_shift(shift_id, update_shift_data)

    @router.put(
        "/{shift_id}/actions/start",
        response_model=ShiftResponse,
        response_model_exclude_none=True,
        status_code=HTTPStatus.OK,
        summary="Старт смены",
        response_description="Информация о запущенной смене",
    )
    async def start_shift(
        self,
        shift_id: UUID,
    ) -> ShiftResponse:
        """Начать смену.

        - **shift_id**: уникальный индентификатор смены
        """
        try:
            shift = await self.shift_service.start_shift(shift_id)
        # TODO изменить на кастомное исключение
        except Exception:
            raise HTTPException(status_code=HTTPStatus.METHOD_NOT_ALLOWED, detail=STR_STATUS_DENIES_START_SHIFT)
        return shift

    @router.get(
        "/{shift_id}/users",
        response_model=Page[ShiftUsersResponse],
        response_model_exclude_none=True,
        status_code=HTTPStatus.OK,
        summary="Получить список пользователей смены",
        response_description="Информация о смене",
    )
    async def get_shift_users(
        self,
        shift_id: UUID,
        pagination: PaginationRequest = Depends()
    ) -> ShiftUsersResponse:
        """
        Получить список пользоватаелй смены.

        - **shift**: Информация о смене
        - **users**: Список всех одобренных пользователей смены.
        """
        return await self.shift_service.get_users_list(shift_id, pagination)

    @router.get(
        '/{shift_id}/requests',
        response_model=list[ShiftDtoRespone],
        response_model_exclude_none=True,
        summary=("Получить информацию обо всех заявках смены" "с возможностью фильтрации"),
        response_description="Полная информация обо заявках смены.",
    )
    async def get_list_all_requests_on_project(
        self,
        shift_id: UUID,
        status: Optional[Request.Status] = None,
    ) -> ShiftDtoRespone:
        """
        Получить сведения обо всех заявках смены.

        Данный метод будет использоваться для получения сведений
        обо всех заявках смены с возможностью фильтрации по:
        номеру смены и статусу заявки.
        - **user_id**: Номер пользователя
        - **name**: Имя пользователя
        - **surname**: Фамилия пользователя
        - **date_of_birth**: Дата рождения пользователя
        - **city**: Город пользователя
        - **phone**: Телефон пользователя
        - **request_id**: Номер заявки
        - **status**: Статус заявки
        """
        return await self.shift_service.list_all_requests(id=shift_id, status=status)
