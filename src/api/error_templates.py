from src.api.response_models.error import ErrorResponse

ERROR_TEMPLATE_FOR_400 = {"description": "Bad Request Response", "model": ErrorResponse}
ERROR_TEMPLATE_FOR_401 = {"description": "Unauthorized", "model": ErrorResponse}
ERROR_TEMPLATE_FOR_403 = {"description": "Forbidden Response", "model": ErrorResponse}
ERROR_TEMPLATE_FOR_404 = {"description": "Not Found Response", "model": ErrorResponse}
ERROR_TEMPLATE_FOR_422 = {"description": "Validation Error Response", "model": ErrorResponse}
