# API de Busca de Operadoras

API para busca de operadores de planos de saúde com base em parâmetros de busca. Projeto desenvolvido para o Teste Técnico da Intuitive Care.

## Visão Geral

Este projeto implementa uma API REST para realizar consultas de operadoras de planos de saúde registradas na ANS (Agência Nacional de Saúde Suplementar). A API permite buscar, filtrar e paginar resultados baseado em diversos parâmetros.

## Arquitetura

O projeto segue os princípios da Arquitetura Limpa (Clean Architecture) com uma estrutura modular:

- **Presentation Layer**
  - `presentation/main.py`: Ponto de entrada principal da aplicação
  - `presentation/api/`: Rotas e dependências da API
  - `presentation/config/`: Configurações da aplicação
  - `presentation/model/`: Modelos de dados para API
  - `presentation/exception/`: Tratamento de exceções padronizado

- **Application Layer**
  - `application/services/`: Serviços com lógica de negócio
  - `application/dto/`: Objetos de transferência de dados
  - `application/exception/`: Exceções de negócio

- **Domain Layer**
  - `domain/entity/`: Entidades de domínio
  - `domain/repository/`: Interfaces dos repositórios

- **Infrastructure Layer**
  - `infra/`: Implementações de persistência, cache e configurações
  - `infra/swagger_config.py`: Configuração centralizada do Swagger

## Stack Tecnológica

- **Python 3.12+**
- **FastAPI**: Framework web para criação de APIs
- **SQLAlchemy**: ORM para acesso ao banco de dados
- **Redis**: Cache para melhorar a performance
- **Pydantic**: Validação de dados e serialização
- **SlowAPI**: Rate limiting para proteção da API
- **Pytest**: Framework de testes

## Recursos

- **Swagger Modular**: Documentação API centralizada e configurável
- **Rate Limiting**: Limite de 100 requisições por minuto por IP
- **CORS**: Suporte completo para requisições cross-origin
- **Respostas Padronizadas**: Formato consistente seguindo RFC 7807 (Problem Details)
- **Cache**: Sistema de cache Redis para consultas frequentes
- **Validação Robusta**: Validação de entrada com mensagens de erro claras
- **Paginação**: Sistema de paginação completo para resultados grandes
- **Ordenação**: Suporte a ordenação por múltiplos campos

## Instalação

### Pré-requisitos

- Python 3.12+
- Pip (gerenciador de pacotes do Python)
- Redis (para cache)
- PostgreSQL (para banco de dados)

### Configuração

1. Clone o repositório:
```bash
git clone TODO ->  Adicionar Repo
cd intuitive-care
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente criando um arquivo `.env` na raiz do projeto:
```
DATABASE_URL=postgresql://usuario:senha@localhost:5432/nome_do_banco
REDIS_URL=redis://localhost:6379/0
ENVIRONMENT=dev
APP_URL=http://localhost:8080
```

## Uso da API

### Principais Endpoints

- **GET /api/v1/operators**: Retorna lista paginada de operadoras
- **GET /api/v1/cache-test**: (Apenas em ambiente dev) Testa o funcionamento do cache

### Parâmetros de Busca

- **query**: Texto para busca em qualquer campo (mínimo 3 caracteres)
- **page**: Número da página (começa em 1)
- **page_size**: Quantidade de resultados por página (1-100)
- **order_by**: Campo para ordenação
- **order_direction**: Direção da ordenação (asc/desc)

### Exemplo de Requisição

```
GET /api/v1/operators?query=Amil&page=1&page_size=10&order_by=corporate_name&order_direction=asc
```

### Exemplo de Resposta

```json
{
  "data": [
    {
      "operator_registry": "123456",
      "tax_identifier": "12345678901234",
      "corporate_name": "Amil Assistência Médica Internacional S.A.",
      "trade_name": "Amil",
      "modality": "Seguradora Especializada em Saúde",
      "street": "Avenida Brasil",
      "number": "1000",
      "complement": "Andar 10",
      "neighborhood": "Centro",
      "city": "São Paulo",
      "state": "SP",
      "zip": "01234567",
      "area_code": "11",
      "phone": "33333333",
      "fax": "33333334",
      "email_address": "contato@amil.com.br",
      "representative": "João Silva",
      "representative_position": "Diretor",
      "sales_region": 1
    }
  ],
  "page": 1,
  "page_size": 10,
  "total_pages": 1,
  "total_items": 1,
  "query": "Amil",
  "order_by": "corporate_name",
  "order_direction": "asc"
}
```

### Cabeçalhos de Resposta

Para requisições sujeitas a rate limiting, a API inclui os seguintes cabeçalhos:

- `X-RateLimit-Limit`: Número máximo de requisições permitidas por período
- `X-RateLimit-Remaining`: Número de requisições restantes no período atual
- `X-RateLimit-Reset`: Tempo (em segundos) até o reset do limite

## Tratamento de Erros

A API segue o formato Problem Details (RFC 7807) para respostas de erro:

```json
{
  "status": 400,
  "type": "http://localhost:8080/parametro-invalido",
  "title": "Parâmetro Inválido",
  "detail": "Propriedade 'order_by' é inválida. Valores permitidos: corporate_name, trade_name, cnpj",
  "timestamp": "2025-03-27T14:30:00Z"
}
```

### Códigos de Status

- **200**: Sucesso
- **400**: Parâmetros inválidos
- **404**: Recurso não encontrado
- **422**: Erro de validação
- **429**: Limite de requisições excedido
- **500**: Erro interno do servidor

## Rate Limiting

A API implementa limitação de taxa para proteger contra uso abusivo:

- **Endpoint `/api/v1/operators`**: 100 requisições por minuto por IP
- Quando o limite é excedido, a API retorna status 429 com headers indicando o tempo de espera

## CORS (Cross-Origin Resource Sharing)

A API suporta CORS, permitindo requisições de diferentes origens:

- Todas as origens são permitidas (`*`)
- Todos os métodos HTTP são aceitos
- Headers relacionados a rate limit são expostos para clientes

## Testes

O projeto inclui uma extensa suíte de testes cobrindo diversos aspectos da API:

- Testes Funcionais
- Testes de Integração
- Testes de Performance
- Testes de Segurança
- Testes de Regressão
- Testes de Fuzzing
- Testes de Conformidade REST
- Testes de Usabilidade

Para executar os testes:

```bash
pytest
```

Para gerar relatório de cobertura:

```bash
pytest --cov=application --cov=domain --cov=presentation
```

## Documentação da API

A documentação interativa da API está disponível nos seguintes endpoints:

- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI Schema**: `/openapi.json`

A documentação foi melhorada para incluir:
- Exemplos detalhados de requisições e respostas
- Descrição completa de todos os modelos
- Documentação de erros em formato Problem Details
- Informações sobre rate limiting

## Cache

A API implementa cache usando Redis para melhorar a performance, com TTL (time-to-live) configurado para requisições frequentes.

## Estrutura do Projeto

```
intuitive-care/
├── application/
│   ├── dto/
│   │   └── operator_model.py
│   ├── exception/
│   │   ├── business_exception.py
│   │   ├── invalid_order_parameter_exception.py
│   │   └── invalid_search_parameter_exception.py
│   └── services/
│       └── operator_service.py
├── domain/
│   └── repository/
│       └── operator_repository.py
├── infra/
│   ├── db_manager.py
│   ├── config.py
│   └── swagger_config.py
├── presentation/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py
│   │   └── routes.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── app_config.py
│   │   ├── limiter_config.py
│   │   └── middleware.py
│   ├── exception/
│   │   ├── api_error.py
│   │   ├── api_error_type.py
│   │   └── exception_handlers.py
│   ├── model/
│   │   ├── operator_request_params.py
│   │   ├── pageable_meta_model.py
│   │   └── pageable_response.py
│   └── main.py
├── tests/
│   ├── test_functional.py
│   ├── test_integration.py
│   ├── test_performance.py
│   └── ...
├── .env
├── requirements.txt
└── README.md
```

## Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Faça commit das suas alterações (`git commit -m 'feat: adiciona nova feature'`)
4. Faça push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Convenções de Commit

O projeto segue a convenção de commits do [Conventional Commits](https://www.conventionalcommits.org/):

- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Alterações na documentação
- `style`: Alterações que não afetam o código (formatação, etc)
- `refactor`: Refatoração de código
- `test`: Adição ou modificação de testes
- `chore`: Alterações no processo de build, ferramentas, etc.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para mais detalhes.

## Autor
Kleber Rhuan
Kleber Rhuan