#!/bin/bash

echo "🚀 Aplicando Migration do Sistema de Chamados"
echo "=============================================="

# Configurações
DB_HOST="localhost"
DB_PORT="5433"
DB_NAME="cidadaoai"
DB_USER="cidadaoai_user"
DB_PASSWORD="cidadaoai_senha_2024"
MIGRATION_FILE="backend/migrations/001_create_chamados_system.sql"

echo "📋 Configurações:"
echo "   Host: $DB_HOST:$DB_PORT"
echo "   Database: $DB_NAME"
echo "   User: $DB_USER"
echo ""

# Verificar se o arquivo de migration existe
if [ ! -f "$MIGRATION_FILE" ]; then
    echo "❌ Arquivo de migration não encontrado: $MIGRATION_FILE"
    exit 1
fi

echo "📄 Arquivo de migration encontrado: $MIGRATION_FILE"
echo ""

# Aplicar migration
echo "🔄 Aplicando migration..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f $MIGRATION_FILE

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migration aplicada com sucesso!"
    echo ""
    echo "🎉 Sistema de Chamados Cidadãos está pronto!"
    echo ""
    echo "📊 Próximos passos:"
    echo "   1. Reiniciar o serviço Docker"
    echo "   2. Testar os novos endpoints"
    echo "   3. Verificar logs do sistema"
    echo ""
    echo "🔗 Endpoints disponíveis:"
    echo "   - GET  /api/chamados/status"
    echo "   - GET  /api/chamados/metrics"
    echo "   - POST /api/chamados/criar"
    echo "   - POST /api/chamados/consultar"
    echo "   - POST /api/chamados/cadastrar-cidadao"
else
    echo ""
    echo "❌ Erro ao aplicar migration!"
    echo ""
    echo "🔍 Verifique:"
    echo "   - Se o PostgreSQL está rodando"
    echo "   - Se as credenciais estão corretas"
    echo "   - Se o banco de dados existe"
    echo ""
    exit 1
fi
