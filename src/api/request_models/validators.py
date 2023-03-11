import re

from pydantic import validator

VALID_NAME_SURNAME = r"^[А-ЯЁ][а-яё]*([-][А-ЯЁ][а-яё]+)*$"
INVALID_TEXT_ERROR = (
    "В поле `{field_name}` может быть использована только кириллица и `-`."
    " Поле `{field_name}` должно начинаться с заглавной буквы."
)
EN_RU = {
    "name": "Имя",
    "surname": "Фамилия",
}


def _is_russian_or_hyphen(value: str, regexp: str, field_name: str) -> str:
    if not re.compile(regexp).match(value):
        message = INVALID_TEXT_ERROR.format(field_name=EN_RU.get(field_name, "Неизвестное поле"))
        raise ValueError(message)
    return value.title()


def name_surname_validator(field_name: str):
    return validator(field_name, allow_reuse=True)(lambda v: _is_russian_or_hyphen(v, VALID_NAME_SURNAME, field_name))
