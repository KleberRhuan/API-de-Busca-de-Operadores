# Documentação da API de Busca de Operadoras

Bem-vindo à documentação da API de Busca de Operadoras. Esta documentação fornece informações detalhadas sobre como utilizar, configurar e contribuir para o projeto.

## Documentos Disponíveis

### Guias de Uso
- [Documentação da API (Swagger)](/docs) - Interface interativa para testar a API
- [Documentação da API (ReDoc)](/redoc) - Documentação alternativa em formato mais legível

### Guias de Configuração
- [Configuração CORS](cors-configuration.md) - Detalhes sobre a implementação CORS na API
- [Instruções Docker](docker-instructions.md) - Como usar o Docker com este projeto
- [Convenção camelCase](camelCase-convention.md) - Detalhes sobre o formato de resposta JSON adotado

### Referências Técnicas
- [README do Projeto](../README.md) - Visão geral do projeto, instalação e uso

## Tópicos Específicos

### CORS e Requisições OPTIONS

O FastAPI e Starlette implementam suporte ao método OPTIONS, essencial para requisições preflight CORS. Para que funcionem corretamente:

1. As requisições devem incluir os cabeçalhos `Origin` e `Access-Control-Request-Method`
2. O servidor deve estar configurado para aceitar o método HTTP desejado
3. Veja mais detalhes em [Configuração CORS](cors-configuration.md)

### Cache e Rate Limiting

A API implementa:

1. Sistema de cache baseado em Redis para melhorar a performance
2. Rate limiting para proteger contra uso excessivo
3. Estes componentes compartilham a mesma conexão Redis quando disponível

### Endpoints Disponíveis

- `GET /api/v1/operators` - Busca operadoras com suporte a filtros e paginação
- Para mais detalhes, consulte a [documentação Swagger](/docs)

### Formato de Resposta JSON - camelCase

A API utiliza o formato camelCase para todas as propriedades JSON nas respostas. Por exemplo:
- `operatorRegistry` em vez de `operator_registry`
- `corporateName` em vez de `corporate_name`
- `representativePosition` em vez de `representative_position`

Esta convenção facilita a integração com clientes frontend que utilizam JavaScript/TypeScript onde camelCase é a convenção padrão.

## Contribuindo com a Documentação

Se você deseja melhorar esta documentação:

1. Faça um fork do repositório
2. Adicione ou atualize os arquivos markdown na pasta `docs/`
3. Envie um Pull Request com suas melhorias 