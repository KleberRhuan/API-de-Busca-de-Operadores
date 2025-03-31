from src.application.exception.business_exception import BusinessException
from src.presentation.exception.api_error import Violation


class ViolationException(BusinessException):
    def __init__(self, field: str, message: str):
        super().__init__("Erro de validação.")
        self.violation = Violation(name=field, message=message)
