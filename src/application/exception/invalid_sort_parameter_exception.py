from src.application.exception.business_exception import BusinessException

class InvalidOrderParameterException(BusinessException):
    def __init__(self, order_by: str, allowed: frozenset[str]):
        self.order_by = order_by
        self.allowed = allowed
        super().__init__(f"Propriedade '{order_by}' é inválida. Valores permitidos: {', '.join(allowed)}")