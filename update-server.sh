#!/bin/bash

echo "🔄 Atualizando Cidadão.AI no servidor..."

# 1. Parar o serviço atual
echo "⏹️ Parando serviço atual..."
docker service rm cidadaoai_cidadaoai_app

# 2. Fazer pull das atualizações
echo "📥 Fazendo pull das atualizações..."
git pull origin main

# 3. Reconstruir a imagem Docker
echo "🔨 Reconstruindo imagem Docker..."
docker build -t cidadaoai:latest .

# 4. Deploy do stack atualizado
echo "🚀 Fazendo deploy do stack atualizado..."
docker stack deploy -c docker-compose.yml cidadaoai

# 5. Verificar status
echo "✅ Verificando status do serviço..."
sleep 10
docker service ls | grep cidadaoai

echo "🎉 Atualização concluída!"
echo "📋 Para ver os logs: docker service logs -f cidadaoai_cidadaoai_app"
