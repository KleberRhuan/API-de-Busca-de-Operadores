from src.application.exception.violation_exception import ViolationException
from src.presentation.exception.api_error import Violation

class InvalidSortParameterException(ViolationException):
    def __init__(self, field: str, message: str):
        super().__init__(field, message)
        