from fastapi import Request

from src.core.exceptions import InvalidSortParameterException


class BaseCBV:
    @staticmethod
    def _check_query_params(request: Request) -> None:
        """Проверка параметров запроса на соответствие разрешенным."""
        allowed_params = set(modelfield.alias for modelfield in request.scope["route"].dependant.query_params)
        for requested_param in request.query_params:
            if requested_param not in allowed_params:
                raise InvalidSortParameterException(requested_param, allowed_params)
