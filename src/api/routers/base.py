from fastapi import Request

from src.core.exceptions import InvalidSortParameterException


class BaseCBV:
    async def check_query_params(self, request: Request) -> None:
        """Проверка парамтров запроса на соответствие разрешенным."""
        allowed_params = [modelfield.alias for modelfield in request.scope["route"].dependant.query_params]
        for requested_param in request.query_params:
            if requested_param not in allowed_params:
                raise InvalidSortParameterException(requested_param, allowed_params)
