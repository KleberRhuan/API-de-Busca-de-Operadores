FROM python:3.12-slim

# Define o nome da imagem
LABEL org.opencontainers.image.title="intuitive-care-backend"
LABEL org.opencontainers.image.description="Backend API for Intuitive Care"
LABEL org.opencontainers.image.vendor="Intuitive Care"

WORKDIR /app

# Instala as dependências do sistema necessárias (com camada otimizada)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    libpq-dev \
    curl \
    bash \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instala o Poetry
RUN pip install --no-cache-dir poetry==2.1.1
RUN pip install --no-cache-dir uvicorn==0.34.0

# Copia apenas os arquivos de dependências primeiro para aproveitar o cache de camadas do Docker
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create true && \
    poetry config virtualenvs.in-project true && \
    poetry install --only main --no-interaction --no-ansi --no-root

# Copia o código da aplicação
COPY . .

# Expõe a porta que a aplicação usará
EXPOSE 8080

# Define variáveis de ambiente para configuração
ENV PYTHONDONTWRITEBYTECODE=1 \
    LOG_LEVEL=INFO \
    PYTHONUNBUFFERED=1 \
    RATE_LIMIT=100 \
    RATE_WINDOW=60 \
    PORT=8080 \
    HOST=0.0.0.0 \
    ENV=dev \
    DATABASE_URL="" \
    REDIS_URL="" \
    CORS_ORIGIN="" \
    REDIS_HOST="" \
    REDIS_PORT="" \
    REDIS_DB=""

# Usuário não-root para segurança
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Verificação de saúde da aplicação
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/v1/health || exit 1

# Comando para iniciar a aplicação
CMD ["/bin/bash", "-c", "source .venv/bin/activate && uvicorn src.presentation.main:application --host 0.0.0.0 --port ${PORT}"]

# Metadados da imagem
LABEL maintainer="Kleber Rhuan"
LABEL version="1.0"
LABEL description="Imagem Docker BackEnd para o Sistema de Cadastro de Operadores" 