from src.application.exception.business_exception import BusinessException


class RateLimitExceededException(BusinessException):
    def __init__(self, limit: int, window: int, reset_in: int):
        self.limit = limit
        self.window = window
        self.reset_in = reset_in
        super().__init__(
            f"Taxa de requisições excedida. Limite de {limit} requisições por {window} segundos. Tente novamente em {reset_in} segundos."
        )
