from src.api.response_models.shift import ErrorResponse

ERROR_TEMPLATE_FOR_400 = {"description": "Bad Request Response", "model": ErrorResponse}
ERROR_TEMPLATE_FOR_401 = {"description": "Unauthorized", "model": ErrorResponse}
ERROR_TEMPLATE_FOR_403 = {"description": "Forbidden Response", "model": ErrorResponse}
ERROR_TEMPLATE_FOR_404 = {"description": "Not Found Response", "model": ErrorResponse}
