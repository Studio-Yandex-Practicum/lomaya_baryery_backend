from pydantic import BaseModel


class AdministratorMailRequestResponse(BaseModel):
    url: str
