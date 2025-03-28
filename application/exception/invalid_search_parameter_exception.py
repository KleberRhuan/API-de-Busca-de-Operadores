from application.exception.business_exception import BusinessException


class InvalidSearchParameterException(BusinessException):
    def __init__(self, request_parameter: str, allowed: set):
        self.request_parameter = request_parameter
        self.allowed = allowed
        super().__init__(f"O parametro de pesquisa '{request_parameter}' é invalido. Valores permitidos: {', '.join(allowed)}")