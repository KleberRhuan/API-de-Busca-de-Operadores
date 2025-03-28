FROM python:3.12-slim

WORKDIR /app

# Instala as dependências do sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Instala o Poetry
RUN pip install --no-cache-dir poetry

# Copia os arquivos do Poetry e instala as dependências
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

# Copia o código da aplicação
COPY . .

# Expõe a porta que a aplicação usará
EXPOSE 8080

# Define variáveis de ambiente para configuração
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production

# Comando para iniciar a aplicação
CMD ["uvicorn", "src.presentation.main:application", "--host", "0.0.0.0", "--port", "8080"] 