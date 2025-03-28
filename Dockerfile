FROM python:3.12-slim

WORKDIR /app

# Instala as dependências do sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de requisitos e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Expõe a porta que a aplicação usará
EXPOSE 8080

# Define variáveis de ambiente para configuração
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production

# Comando para iniciar a aplicação
CMD ["uvicorn", "presentation.main:application", "--host", "0.0.0.0", "--port", "8080"] 