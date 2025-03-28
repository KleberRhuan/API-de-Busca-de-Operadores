# Configuração CORS na API

Este documento detalha como o Cross-Origin Resource Sharing (CORS) é implementado e configurado na API de Busca de Operadoras.

## O que é CORS?

CORS (Cross-Origin Resource Sharing) é um mecanismo baseado em cabeçalhos HTTP que permite que um servidor indique qualquer origem (domínio, esquema ou porta) diferente da sua própria, a partir da qual um navegador deve permitir o carregamento de recursos.

## Implementação na API

A API utiliza o middleware CORS fornecido pelo FastAPI, que é baseado no middleware do Starlette. A configuração é feita no arquivo `src/infra/middleware/cors_middleware.py`.

### Configuração Atual

```python
def setup_cors(app: FastAPI) -> FastAPI:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["localhost"],
        allow_credentials=True,
        allow_methods=["GET", "OPTIONS"],
        allow_headers=["Accept", "Content-Type"],
        expose_headers=[
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
            "Retry-After"
        ],
    )
    return app
```

## Principais Aspectos da Configuração

### Origens Permitidas

Por padrão, apenas `localhost` está configurado como origem permitida. Para ambientes de produção, esta configuração deve ser ampliada para incluir os domínios específicos que acessarão a API.

### Métodos Permitidos

Atualmente, apenas os métodos `GET` e `OPTIONS` são permitidos. O método `OPTIONS` é essencial para suportar requisições preflight, que são usadas pelos navegadores para determinar se a requisição real é segura para ser enviada.

### Cabeçalhos Permitidos

Os cabeçalhos `Accept` e `Content-Type` são permitidos nas requisições. Cabeçalhos adicionais podem ser necessários dependendo da implementação do cliente.

### Cabeçalhos Expostos

A API expõe os seguintes cabeçalhos relacionados ao rate limiting:
- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`
- `Retry-After`

Estes cabeçalhos permitem que o cliente esteja ciente das limitações de taxa e se adapte apropriadamente.

## Requisições Preflight (OPTIONS)

O FastAPI e o Starlette implementam suporte ao método HTTP OPTIONS, que é essencial para as requisições preflight CORS. No entanto, para que essas requisições sejam tratadas corretamente, os clientes devem incluir dois cabeçalhos específicos:

1. `Origin`: Indica a origem da requisição
2. `Access-Control-Request-Method`: Indica o método HTTP da requisição real que seguirá

Sem estes cabeçalhos, a requisição preflight pode não ser processada corretamente, resultando em erros CORS no navegador.

### Exemplo de Requisição Preflight

```http
OPTIONS /api/v1/operators HTTP/1.1
Host: api.exemplo.com
Origin: https://exemplo.com
Access-Control-Request-Method: GET
Access-Control-Request-Headers: Content-Type
```

### Resposta Esperada

```http
HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://exemplo.com
Access-Control-Allow-Methods: GET, OPTIONS
Access-Control-Allow-Headers: Content-Type
Access-Control-Allow-Credentials: true
Access-Control-Max-Age: 600
```

## Personalização da Configuração CORS

Para personalizar a configuração CORS, você pode ajustar os seguintes aspectos:

1. **Origens Permitidas**: Adicione domínios específicos na lista `allow_origins`
2. **Métodos HTTP**: Adicione ou remova métodos na lista `allow_methods`
3. **Cabeçalhos Permitidos**: Adicione cabeçalhos necessários em `allow_headers`
4. **Credenciais**: Configure `allow_credentials` como `True` para permitir o envio de cookies

## Testes CORS

A API inclui testes CORS completos que verificam:
- Origens permitidas e não permitidas
- Cabeçalhos corretos nas respostas
- Comportamento adequado para requisições preflight
- Exposição correta de cabeçalhos

Para executar os testes CORS:

```bash
poetry run pytest tests/test_cors.py
``` 