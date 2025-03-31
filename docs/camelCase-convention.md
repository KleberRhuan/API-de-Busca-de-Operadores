# Convenção camelCase na API

## Visão Geral

Esta API adota a convenção de nomenclatura camelCase para todas as propriedades nas respostas JSON. Isso significa que os nomes de propriedades começam com letra minúscula e as palavras subsequentes iniciam com letra maiúscula, sem espaços ou outros separadores.

## Exemplos

Abaixo estão exemplos de como as propriedades são formatadas na resposta da API:

| Nome no Código (snake_case) | Nome na Resposta (camelCase) |
|----------------------------|------------------------------|
| operator_registry         | operatorRegistry             |
| corporate_name            | corporateName                |
| trade_name               | tradeName                    |
| representative_position   | representativePosition       |
| sales_region             | salesRegion                  |
| registration_date        | registrationDate             |
| area_code                | areaCode                     |

## Por que camelCase?

A escolha do formato camelCase para respostas JSON foi feita por várias razões:

1. **Compatibilidade com Frontend**: A maioria das linguagens e frameworks de frontend (JavaScript, TypeScript, React, Angular, Vue) utiliza camelCase como convenção. Isso facilita a integração e reduz a necessidade de conversão de formatos.

2. **Padrão JSON**: Enquanto a linguagem Python prefere snake_case (usando underscores), o camelCase é amplamente adotado na comunidade JSON como uma convenção.

3. **Clareza na API**: Manter uma convenção consistente em toda a API proporciona uma experiência mais previsível para os desenvolvedores que a utilizam.

## Implementação

A conversão de snake_case para camelCase é feita automaticamente usando os recursos do Pydantic:

```python
from pydantic import BaseModel
from pydantic.alias_generators import to_camel

class SomeModel(BaseModel):
    model_config = {
        "populate_by_name": True,
        "alias_generator": to_camel
    }
    
    some_field: str
    another_field: int
    
# Resultado JSON: {"someField": "valor", "anotherField": 123}
```

Nas requisições à API, você pode utilizar tanto o formato snake_case quanto camelCase nos parâmetros de consulta, mas as respostas sempre retornarão em camelCase. 