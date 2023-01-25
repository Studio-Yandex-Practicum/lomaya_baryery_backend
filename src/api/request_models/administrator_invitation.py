from pydantic import EmailStr

from src.api.request_models.request_base import RequestBase


class AdministratorInvitationRequest(RequestBase):
    name: str
    surname: str
    email: EmailStr
