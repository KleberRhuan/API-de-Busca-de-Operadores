from typing import Dict, Any, Type


class ErrorMessageTranslator:
    """
    Classe responsável por traduzir mensagens de erro para português.
    """
    
    # Dicionário de traduções para mensagens comuns
    _translations: Dict[str, str] = {
        "value is not a valid integer": "O valor não é um número inteiro válido",
        "field required": "Campo obrigatório",
        "string too short": "Texto muito curto",
        "string too long": "Texto muito longo",
        "invalid value": "Valor inválido",
        "extra fields not permitted": "Campos extras não são permitidos",
        "value is not a valid email address": "E-mail inválido"
    }
    
    # Dicionário simplificado para tipos de erro
    _type_translations: Dict[str, str] = {
        "int_parsing": "Este campo deve ser um número inteiro",
        "missing": "Este campo é obrigatório",
        "literal_error": "O valor não está entre as opções permitidas, verifique a documentação da API."
    }
    
    @classmethod
    def translate(cls, error: Dict[str, Any]) -> str:
        """
        Traduz uma mensagem de erro para português de forma simplificada.
        """
        error_type = error.get("type", "")
        error_msg = error.get("msg", "")
        field_loc = error.get("loc", [])
        field_name = field_loc[-1] if field_loc else ""

        # Verificar se temos tradução específica para o tipo de erro
        if error_type in cls._type_translations:
            return f"{cls._type_translations[error_type]}"
            
        # Tradução genérica baseada na mensagem de erro
        translated_message = cls._translations.get(error_msg.lower(), error_msg)
        return f"{translated_message}"
    
    @classmethod
    def add_translation(cls, original: str, translation: str) -> None:
        """
        Adiciona uma nova tradução ao dicionário.
        """
        cls._translations[original.lower()] = translation
    
    @classmethod
    def add_field_name(cls, field: str, friendly_name: str) -> None:
        """
        Adiciona um nome amigável para um campo.
        """
        cls._field_names[field] = friendly_name

def get_translator() -> Type[ErrorMessageTranslator]:
    """Função para obter o tradutor de mensagens de erro."""
    return ErrorMessageTranslator