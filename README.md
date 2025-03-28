# Intuitive Care API

API de busca de operadoras de saúde desenvolvida com FastAPI, oferecendo uma interface intuitiva e eficiente para consulta de informações sobre operadoras.

## 🚀 Tecnologias

- Python 3.12+
- FastAPI
- SQLAlchemy
- Redis (Cache)
- Limits (Rate Limiting)
- PostgreSQL
- Poetry (Gerenciamento de Dependências)
- Pytest (Testes)

## 📋 Pré-requisitos

- Python 3.12 ou superior
- Poetry
- PostgreSQL
- Redis (opcional, para cache e rate limiting)

## 🛠️ Instalação

1. Clone o repositório:
```bash
git clone https://github.com/KleberRhuan/API-de-Busca-de-Operadores
cd intuitive-care
```

2. Instale as dependências com Poetry:
```bash
poetry install
```

3. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

4. Configure o banco de dados:
```bash
# Execute as migrações (quando implementadas)
poetry run alembic upgrade head
```

## 🐳 Utilizando Docker

Para executar o projeto usando Docker:

```bash
# Desenvolvimento
docker-compose -f docker-compose.dev.yml up -d

# Produção
docker-compose up -d
```

Consulte o arquivo [docs/docker-instructions.md](docs/docker-instructions.md) para instruções detalhadas sobre Docker.

## 🏗️ Estrutura do Projeto

```
intuitive-care/
├── src/
│   ├── application/
│   │   ├── service/
│   │   │   └── operator_service.py
│   │   ├── exception/
│   │   │   ├── business_exception.py
│   │   │   ├── invalid_sort_parameter_exception.py
│   │   │   └── rate_limit_exception.py
│   │   └── dto/
│   │       └── operator_model.py
│   ├── domain/
│   │   ├── model/
│   │   │   └── operator.py
│   │   └── repository/
│   │       └── operator_repository.py
│   ├── infra/
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   └── swagger_config.py
│   │   ├── database/
│   │   │   └── __init__.py
│   │   │   └── cache_key_manager.py
│   │   └── middleware/
│   │       ├── cors_middleware.py
│   │       └── rate_limit_middleware.py
│   └── presentation/
│       ├── api/
│       │   └── routes.py
│       ├── exception/
│       │   ├── api_error.py
│       │   ├── api_error_type.py
│       │   ├── error_message_translator.py
│       │   └── exception_handlers.py
│       ├── model/
│       │   ├── operator_request_params.py
│       │   └── pageable_response.py
│       └── main.py
├── tests/
│   ├── conftest.py
│   ├── test_functional.py
│   ├── test_integration.py
│   ├── test_performance.py
│   ├── test_security.py
│   ├── test_usability.py
│   ├── test_regression.py
│   ├── test_conformity.py
│   ├── test_fuzzing.py
│   ├── test_rate_limiting.py
│   ├── test_cors.py
│   ├── test_app_config.py
│   └── test_exception_handlers.py
├── pyproject.toml
├── README.md
└── .env
```

## 🚀 Executando o Projeto

1. Inicie o servidor de desenvolvimento:
```bash
poetry run start
```

2. Acesse a documentação da API:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🧪 Testes

Execute os testes:
```bash
# Todos os testes
poetry run test

# Testes com cobertura
poetry run pytest --cov=src tests/

# Testes específicos
poetry run pytest tests/test_functional.py
```

## 📝 Endpoints

### GET /api/v1/operators

Busca operadoras de saúde com filtros e paginação.

**Parâmetros:**
- `query`: Texto para busca (mínimo 3 caracteres)
- `page`: Número da página (default: 1)
- `page_size`: Itens por página (default: 10, max: 100)
- `order_by`: Campo para ordenação
- `order_direction`: Direção da ordenação (asc/desc)

**Exemplo de resposta:**
```json
{
    "data": [
        {
            "id": 1,
            "corporate_name": "Nome da Operadora",
            "trade_name": "Nome Fantasia",
            "cnpj": "12345678901234"
        }
    ],
    "meta": {
        "total": 100,
        "page": 1,
        "page_size": 10,
        "total_pages": 10
    }
}
```

## 🔒 Segurança e Otimizações

### Rate Limiting
- Implementação moderna usando a biblioteca `limits`
- Limite configurável via variáveis de ambiente
- Cabeçalhos compatíveis com RFC 6585
- Suporte para diferentes tipos de storage (Memory/Redis)
- Detecção inteligente de IPs com suporte a proxies
- Tratamento padronizado via sistema de exceções

### Pool de Conexões SQLAlchemy
- Pool de conexões otimizado para performance
- Configuração de timeout, recycle e max_overflow
- Verificação de conexões ativas com pool_pre_ping
- Gerenciamento automático do ciclo de vida das sessões

### CORS
- Configuração completa de CORS para acesso cross-origin
- Suporte para preflight requests (OPTIONS)
- Headers personalizáveis via variáveis de ambiente
- Suporte a OPTIONS, mas as requisições precisam ter os headers `Origin` e `Access-Control-Request-Method` configurados corretamente

### Sistema de Cache
- Cache implementado com Redis para queries frequentes
- Centralização da configuração do Redis
- Compartilhamento da conexão Redis entre cache e rate limiting
- TTL configurável para diferentes tipos de consultas

## 🛠️ Desenvolvimento

### Formatação de Código
```bash
# Formatar código
poetry run format

# Ordenar imports
poetry run sort

# Verificar estilo
poetry run lint
```

### Adicionando Novas Dependências
```bash
# Dependência de produção
poetry add nome-do-pacote

# Dependência de desenvolvimento
poetry add --group dev nome-do-pacote
```

## 📦 Deploy

1. Configure as variáveis de ambiente de produção
2. Execute as migrações do banco de dados
3. Inicie o servidor com:
```bash
poetry run uvicorn src.presentation.main:app --host 0.0.0.0 --port 8000
```

Ou utilize Docker:
```bash
docker-compose up -d
```

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👥 Autores

- Kleber Rhuan - [@kleberrhuan](https://github.com/kleberrhuan)

## 🙏 Agradecimentos

- FastAPI
- SQLAlchemy
- Pydantic
- E todos os outros projetos open source utilizados
