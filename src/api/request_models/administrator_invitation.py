from pydantic import EmailStr, Field, StrictStr

from src.api.request_models.request_base import RequestBase
from src.api.request_models.validators import name_surname_validator


class AdministratorInvitationRequest(RequestBase):
    name: StrictStr = Field(min_length=2, max_length=20)
    surname: StrictStr = Field(min_length=2, max_length=100)
    email: EmailStr

    _validate_name = name_surname_validator("name")
    _validate_surname = name_surname_validator("surname")
