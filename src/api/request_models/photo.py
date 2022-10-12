from src.api.request_models.request_base import RequestBase


class PhotoCreateRequest(RequestBase):
    url: str


class PhotoUpdateRequest(PhotoCreateRequest):
    pass
