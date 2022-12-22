from typing import Optional

from src.api.request_models.request_base import RequestBase


class RequestDeclineRequest(RequestBase):
    message: Optional[str] = None
