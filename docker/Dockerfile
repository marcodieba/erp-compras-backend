# Usa uma imagem oficial leve do Python
FROM python:3.12-slim

# Evita que o Python escreva ficheiros .pyc e força os logs a irem direto para o terminal
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema necessárias
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia os requirements e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do código
COPY . .

# CORREÇÃO: Criar as pastas necessárias para evitar erros de FileNotFoundError
RUN mkdir -p logs media

# Comando padrão
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]