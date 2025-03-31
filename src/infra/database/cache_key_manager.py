from src.presentation.model.operator_request_params import \
    OperatorRequestParams


def operator_key_builder(func, *args, **kwargs):
    """
    Método para gerar a chave de cache com base nos parâmetros de busca.
    Com o decorador @cached, os argumentos são passados da seguinte forma:
    - args[0]: a instância do serviço (self)
    - args[1]: o primeiro argumento do método (criteria)
    - kwargs: quaisquer argumentos nomeados adicionais
    """

    if len(args) < 2:
        raise ValueError("Erro ao gerar key do cache: argumentos insuficientes.")

    criteria = args[1]

    if not isinstance(criteria, OperatorRequestParams):
        raise ValueError(
            "Erro ao gerar key do cache: o parâmetro 'criteria' deve ser do tipo OperatorRequestParams."
        )

    try:
        criteria_json = criteria.model_dump_json()
    except AttributeError:
        # Fallback para versões anteriores do Pydantic
        criteria_json = criteria.json()

    return f"operator_search:{criteria_json}"
