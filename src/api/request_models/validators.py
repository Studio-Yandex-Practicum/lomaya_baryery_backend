import re

from pydantic import validator

VALID_NAME_SURNAME = r"^[А-ЯЁ][а-яё]*([-][А-ЯЁ][а-яё]+)*$"
INVALID_TEXT_ERROR = (
    "В поле `{field_name}` могут быть использованы только русские буквы и `-`."
    "Поле `{field_name}` должно начинаться с заглавной буквы."
)
EN_RU = {
    "name": "Имя",
    "surname": "Фамилия",
}


def _is_russian_or_hyphen_or_len(value: str, regexp: str, field_name: str) -> str:
    if not re.compile(regexp).match(value):
        message = INVALID_TEXT_ERROR.format(field_name=EN_RU.get(field_name, "Неизвестное поле"))
        raise ValueError(message)
    if field_name == 'name' and (len(value) > 20 or len(value) < 2):
        raise ValueError('Длина поля Имя должна быть от 2 до 20 символов.')
    return value.title()


def name_surname_validator(field_name: str):
    return validator(field_name, allow_reuse=True)(lambda v: _is_russian_or_hyphen_or_len(v, VALID_NAME_SURNAME, field_name))
