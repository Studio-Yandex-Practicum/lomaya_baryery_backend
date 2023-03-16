from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING, Any, Dict
from uuid import UUID

from fastapi import HTTPException

if TYPE_CHECKING:
    from src.core.db.models import Base as DatabaseModel


class ApplicationError(HTTPException):
    """Собственное исключение для бизнес-логики приложения."""

    status_code: int = None
    detail: str = "О! Какая-то неопознанная ошибка. Мы её обязательно опознаем и исправим!"
    headers: Dict[str, Any] = None

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail, headers=self.headers)


class NotValidValueError(ApplicationError):
    """Исключение для невалидных данных."""

    def __init__(self, detail: str | None) -> None:
        self.detail = detail
        super().__init__()


class CurrentTaskNotFoundError(ApplicationError):
    """Не найдено текущей задачи для пользователя."""

    detail = "Сейчас заданий нет."


class TodayTaskNotFoundError(ApplicationError):
    """Не найдено ежедневной задачи на текущий день."""

    detail = "Не найдено ежедневной задачи на текущий день."


class CannotAcceptReportError(ApplicationError):
    """Статус задания пользователя не позволяет выполнить операцию."""

    detail = "Ранее отправленный отчет проверяется или уже принят. Новые отчеты сейчас не принимаются."


class DuplicateReportError(ApplicationError):
    """Отчет с таким фото уже отправлялся ранее."""

    detail = "Данная фотография уже использовалась в другом отчёте. Пожалуйста, загрузите другую фотографию."


class ExceededAttemptsReportError(ApplicationError):
    """Превышено количество попыток сдать отчет."""

    detail = (
        "Превышено количество попыток сдать отчет."
        "Предлагаем продолжить, ведь впереди много интересных заданий. "
        "Следующее задание придет в 8.00 мск."
    )


class EmptyReportError(ApplicationError):
    """Отчет должен содержать фото."""

    detail = "Отчет должен содержать фото."


class ReportSkippedError(ApplicationError):
    """Отчет пропущен."""

    detail = "Задание было пропущено, следующее задание придет в 8.00 мск."


class NotFoundError(ApplicationError):
    def __init__(self, object_name: str, object_id: UUID):
        self.status_code = HTTPStatus.NOT_FOUND
        self.detail = "Объект {} с id: {} не найден".format(object_name, object_id)


class AlreadyExistsError(ApplicationError):
    def __init__(self, obj: DatabaseModel):
        self.status_code = HTTPStatus.BAD_REQUEST
        self.detail = f"Объект {obj} уже существует"


class ShiftStartForbiddenError(ApplicationError):
    def __init__(self, shift_name: str, shift_id: UUID):
        self.status_code = HTTPStatus.BAD_REQUEST
        self.detail = f"Невозможно начать смену {shift_name} с id: {shift_id}. Проверьте статус смены"


class ShiftFinishForbiddenError(ApplicationError):
    def __init__(self, shift_name: str, shift_id: UUID):
        self.status_code = HTTPStatus.BAD_REQUEST
        self.detail = f"Невозможно завершить смену {shift_name} с id: {shift_id}. Проверьте статус смены"


class ShiftCancelForbiddenError(ApplicationError):
    def __init__(self, shift_name: str, shift_id: UUID):
        self.status_code = HTTPStatus.BAD_REQUEST
        self.detail = f"Невозможно отменить смену {shift_name} с id: {shift_id}. Проверьте статус смены"


class SendTelegramNotifyError(ApplicationError):
    """Невозможно отправить сообщение в telegram."""

    def __init__(self, user_id: UUID, user_name: str, surname: str, telegram_id: int, exc: Exception):
        self.status_code = HTTPStatus.BAD_REQUEST
        self.detail = (
            f"Возникла ошибка '{exc}' при отправке сообщения пользователю -"
            f" id: {user_id}, Имя: {user_name}, Фамилия: {surname}, Телеграм id: {telegram_id}"
        )


class ReportAlreadyReviewedError(ApplicationError):
    def __init__(self, status: UUID):
        self.status_code = HTTPStatus.FORBIDDEN
        self.detail = "Задание уже проверено, статус задания: {}.".format(status)


class ReportWaitingPhotoError(ApplicationError):
    status_code = HTTPStatus.NOT_FOUND
    detail = "К заданию нет отчета участника."


class CreateShiftForbiddenError(ApplicationError):
    def __init__(self, detail: str):
        self.status_code = HTTPStatus.FORBIDDEN
        self.detail = detail


class ShiftUpdateError(ApplicationError):
    def __init__(self, detail: str):
        self.status_code = HTTPStatus.BAD_REQUEST
        self.detail = detail


class UpdateShiftForbiddenError(ApplicationError):
    def __init__(self, detail: str):
        self.status_code = HTTPStatus.FORBIDDEN
        self.detail = detail


class ShiftsDatesIntersectionError(ApplicationError):
    status_code = HTTPStatus.BAD_REQUEST
    detail = "Дата окончания текущей смены не может равняться или быть больше даты начала новой смены"


class GetStartedShiftError(ApplicationError):
    def __init__(self, detail: str):
        self.status_code = HTTPStatus.NOT_FOUND
        self.detail = detail


class RegistrationForbidenError(ApplicationError):  # noqa N818
    status_code = HTTPStatus.FORBIDDEN
    detail = (
        "К сожалению, на данный момент мы не можем зарегистрировать вас в проекте: смена уже "
        "началась и группа участников набрана. Чтобы не пропустить актуальные новости "
        "Центра \"Ломая барьеры\" - вступайте в нашу группу ВКонтакте https://vk.com/socialrb02"
    )


class AlreadyRegisteredError(ApplicationError):  # noqa N818
    status_code = HTTPStatus.OK
    detail = (
        "Вы уже зарегистрированы в проекте, ожидайте свое первое задание "
        "в день старта смены. Актуальную дату начала смены вы можете "
        "посмотреть в нашей группе ВКонтакте https://vk.com/socialrb02"
    )


class RequestAlreadyReviewedError(ApplicationError):
    def __init__(self, status):
        self.status_code = HTTPStatus.FORBIDDEN
        self.detail = "Заявка на участие уже проверена, статус заявки: {}.".format(status)


class RequestForbiddenError(ApplicationError):  # noqa N818
    status_code = HTTPStatus.FORBIDDEN
    detail = (
        "К сожалению, на данный момент мы не можем зарегистрировать вас на текущую смену. "
        "Чтобы не пропустить актуальные новости Центра \"Ломая барьеры\" - вступайте "
        "в нашу группу ВКонтакте https://vk.com/socialrb02"
    )


class InvalidAuthenticationDataError(ApplicationError):
    """Введены неверные данные для аутентификации."""

    status_code = HTTPStatus.BAD_REQUEST
    detail = "Неверный email или пароль."


class AdministratorBlockedError(ApplicationError):
    """Попытка аутентификации заблокированного пользователя."""

    status_code = HTTPStatus.FORBIDDEN
    detail = "Пользователь заблокирован."


class UnauthorizedError(ApplicationError):
    """Пользователь не авторизован."""

    status_code = HTTPStatus.UNAUTHORIZED
    detail = "У Вас нет прав для просмотра запрошенной страницы."


class AdministratorNotFoundError(ApplicationError):
    """Пользователь не найден."""

    status_code = HTTPStatus.BAD_REQUEST
    detail = "Пользователь с указанными реквизитами не найден."


class AdministratorAlreadyExistsError(ApplicationError):
    """Пользователь с таким email уже существует."""

    status_code = HTTPStatus.BAD_REQUEST
    detail = "Администратор с указанным email уже существует."


class AdministratorInvitationInvalid(ApplicationError):  # noqa N818
    status_code = HTTPStatus.BAD_REQUEST
    detail = "Указанный код регистрации неверен или устарел."


class EmailSendError(ApplicationError):
    def __init__(self, recipients: list[str], exc: Exception):
        self.status_code = HTTPStatus.BAD_REQUEST
        self.detail = f"Возникла ошибка {exc} при отправке email на адрес {recipients}."


class InvalidDateFormatError(ApplicationError):
    status_code = HTTPStatus.BAD_REQUEST
    detail = "Некорректный формат даты. Ожидаемый формат: YYYY-MM-DD."


class InvitationAlreadyDeactivated(ApplicationError):
    status_code = HTTPStatus.FORBIDDEN
    detail = "Приглашение уже деактивировано"


class InvitationAlreadyActivated(ApplicationError):
    status_code = HTTPStatus.FORBIDDEN
    detail = "Приглашение активно"
