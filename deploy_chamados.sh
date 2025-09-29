#!/bin/bash

echo "🚀 DEPLOY SISTEMA DE CHAMADOS - FASE 1"
echo "======================================"

# Configurações do servidor
SERVER="root@212.85.0.166"
PROJECT_PATH="/root/projetos/cidadaoai-chatwoot"

echo "📡 Conectando ao servidor..."
echo ""

# Comandos para executar no servidor
ssh $SERVER << 'EOF'
    echo "🔄 Atualizando código do repositório..."
    cd /root/projetos/cidadaoai-chatwoot
    git pull origin main
    
    echo ""
    echo "📦 Instalando nova dependência (asyncpg)..."
    source venv/bin/activate
    pip install asyncpg==0.29.0
    
    echo ""
    echo "🗄️ Aplicando migration do sistema de chamados..."
    chmod +x apply_migration.sh
    ./apply_migration.sh
    
    echo ""
    echo "🔄 Reiniciando serviços Docker..."
    docker stack deploy -c docker-compose.yml cidadaoai
    
    echo ""
    echo "⏳ Aguardando serviços iniciarem..."
    sleep 30
    
    echo ""
    echo "🔍 Verificando status dos serviços..."
    docker service ls --filter name=cidadaoai
    
    echo ""
    echo "✅ Deploy concluído!"
    echo ""
    echo "🧪 Testando endpoints do sistema de chamados..."
    echo ""
    
    echo "Status do sistema:"
    curl -s https://tecnico.sisgov.app.br/api/chamados/status | jq .
    
    echo ""
    echo "Métricas do sistema:"
    curl -s https://tecnico.sisgov.app.br/api/chamados/metrics | jq .
    
    echo ""
    echo "🎉 Sistema de Chamados Cidadãos está online!"
    echo ""
    echo "📊 Endpoints disponíveis:"
    echo "  - GET  /api/chamados/status"
    echo "  - GET  /api/chamados/metrics"
    echo "  - POST /api/chamados/criar"
    echo "  - POST /api/chamados/consultar"
    echo "  - POST /api/chamados/cadastrar-cidadao"
    echo ""
    echo "📚 Documentação:"
    echo "  - docs/MANUAL_IMPLEMENTACAO_FASE1.md"
    echo "  - docs/fluxo_sistema.md"
    echo "  - docs/database_schema.sql"
EOF

echo ""
echo "🎯 Deploy concluído com sucesso!"
echo ""
echo "🔗 Acesse: https://tecnico.sisgov.app.br"
echo "📊 Status: https://tecnico.sisgov.app.br/api/chamados/status"
echo "📈 Métricas: https://tecnico.sisgov.app.br/api/chamados/metrics"
echo ""
echo "🤖 Sistema de Chamados Cidadãos está pronto para uso!"
