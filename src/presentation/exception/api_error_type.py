from enum import Enum


class ApiErrorType(str, Enum):
    METHOD_NOT_ALLOWED = ("/metodo-invalido", "Método Inválido")
    MESSAGE_NOT_READABLE = ("/mensagem-incompreensivel", "Mensagem Incompreensível")
    RESOURCE_NOT_FOUND = ("/recurso-nao-encontrado", "Recurso Não Encontrado")
    INVALID_PARAMETER = ("/parametro-invalido", "Parâmetro Inválido")
    SYSTEM_ERROR = ("/erro-interno", "Erro Interno do Sistema")
    RATE_LIMIT_EXCEEDED = (
        "/limite-de-requisicoes-excedido",
        "Limite de Requisições Excedido",
    )

    def __new__(cls, uri, title):
        obj = str.__new__(cls, uri)
        obj._value_ = uri
        obj.title = title
        return obj

    def as_dict(self):
        return {"type": self.value, "title": self.title}
