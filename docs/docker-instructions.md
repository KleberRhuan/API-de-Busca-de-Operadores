# Instruções para Docker

Este documento contém instruções detalhadas para construir, executar e gerenciar a aplicação usando Docker.

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Configuração Rápida

Para iniciar a aplicação completa com banco de dados e cache:

```bash
docker-compose up -d
```

A API estará disponível em: http://localhost:8080/docs

## Construindo a Imagem Docker

Se quiser construir apenas a imagem Docker da API:

```bash
docker build -t intuitive-care-api .
```

## Executando os Contêineres Individualmente

### API

```bash
docker run -d \
  --name intuitive-care-api \
  -p 8080:8080 \
  -e DATABASE_URL=postgresql://postgres:postgres@postgres:5432/operators_db \
  -e REDIS_URL=redis://redis:6379/0 \
  -e ENVIRONMENT=production \
  --network app-network \
  intuitive-care-api
```

### PostgreSQL

```bash
docker run -d \
  --name intuitive-care-postgres \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=operators_db \
  -v postgres_data:/var/lib/postgresql/data \
  --network app-network \
  postgres:15-alpine
```

### Redis

```bash
docker run -d \
  --name intuitive-care-redis \
  -p 6379:6379 \
  -v redis_data:/data \
  --network app-network \
  redis:7-alpine
```

## Comando Úteis

### Verificar Logs

```bash
# Logs da API
docker logs intuitive-care-api

# Logs do PostgreSQL
docker logs intuitive-care-postgres

# Logs do Redis
docker logs intuitive-care-redis

# Logs de todos os serviços no Docker Compose
docker-compose logs -f
```

### Acessar o Terminal dos Contêineres

```bash
# Terminal da API
docker exec -it intuitive-care-api bash

# Terminal do PostgreSQL
docker exec -it intuitive-care-postgres psql -U postgres -d operators_db

# Terminal do Redis
docker exec -it intuitive-care-redis redis-cli
```

### Parar e Remover Contêineres

```bash
# Parar e remover com Docker Compose
docker-compose down

# Parar e remover incluindo volumes
docker-compose down -v
```

## Variáveis de Ambiente

A aplicação suporta as seguintes variáveis de ambiente que podem ser configuradas no arquivo `.env` ou passadas diretamente para o contêiner:

| Variável        | Descrição                            | Valor Padrão                                         |
|-----------------|--------------------------------------|------------------------------------------------------|
| DATABASE_URL    | URL de conexão com o banco de dados  | postgresql://postgres:postgres@postgres:5432/operators_db |
| REDIS_URL       | URL de conexão com o Redis           | redis://redis:6379/0                                |
| ENVIRONMENT     | Ambiente de execução                 | production                                           |

## Desenvolvimento com Docker

Para desenvolvimento, você pode montar o diretório local como um volume:

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

Isso permitirá que você edite os arquivos localmente e as alterações serão refletidas imediatamente no contêiner.

## Solução de Problemas

### Conexão com o Banco de Dados Falha

Verifique se o PostgreSQL está em execução e acessível:

```bash
docker exec -it intuitive-care-postgres pg_isready
```

### Conexão com o Redis Falha

Verifique se o Redis está em execução e acessível:

```bash
docker exec -it intuitive-care-redis redis-cli ping
```

### Problemas de Permissão com Volumes

Se encontrar problemas de permissão com volumes, tente:

```bash
# Recrie os volumes
docker-compose down -v
docker-compose up -d

# Ou ajuste as permissões nos contêineres
docker exec -it intuitive-care-api chown -R 1000:1000 /app
``` 