FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de requisitos primeiro (para melhor cache)
COPY requirements*.txt ./

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir python-socketio==5.11.1 aiohttp==3.9.3 websockets==12.0

# Criar diretório para arquivos de mídia
RUN mkdir -p /app/media/audio

# Copiar código fonte
COPY . .

# Instalar o pacote em modo desenvolvimento
RUN pip install -e .

# Expor porta
EXPOSE 8000

# Comando para iniciar
CMD ["python", "-m", "backend.main"]