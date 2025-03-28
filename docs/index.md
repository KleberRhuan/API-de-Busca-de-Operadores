# Documentação da API de Busca de Operadoras

Bem-vindo à documentação da API de Busca de Operadoras. Esta documentação fornece informações detalhadas sobre como utilizar, configurar e contribuir para o projeto.

## Documentos Disponíveis

### Guias de Uso
- [Documentação da API (Swagger)](/docs) - Interface interativa para testar a API
- [Documentação da API (ReDoc)](/redoc) - Documentação alternativa em formato mais legível

### Guias de Configuração
- [Configuração CORS](cors-configuration.md) - Detalhes sobre a implementação CORS na API
- [Instruções Docker](docker-instructions.md) - Como usar o Docker com este projeto

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

## Contribuindo com a Documentação

Se você deseja melhorar esta documentação:

1. Faça um fork do repositório
2. Adicione ou atualize os arquivos markdown na pasta `docs/`
3. Envie um Pull Request com suas melhorias 