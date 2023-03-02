from fastapi import Request

from src.core.exceptions import InvalidSortParameterException


class BaseCBV:
    request: Request

    async def check_query_params(self) -> None:
        """Проверка парамтров запроса на соответствие разрешенным."""
        allowed_params = [modelfield.alias for modelfield in self.request.scope["route"].dependant.query_params]
        for requested_param in self.request.query_params:
            if requested_param not in allowed_params:
                raise InvalidSortParameterException
