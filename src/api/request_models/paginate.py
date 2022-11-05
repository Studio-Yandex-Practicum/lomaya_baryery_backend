from pydantic import Field, BaseModel


class PaginationRequest(BaseModel):
    limit: int = Field(min=1, max=50)
    offset: int = Field(min=1, max=100)