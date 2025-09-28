#!/bin/bash

# Script para monitorar apenas logs da IA de forma limpa
# Uso: ./monitor_ai_logs.sh

echo "🤖 Monitor de Logs da IA - Cidadão.AI"
echo "======================================"
echo "Pressione Ctrl+C para sair"
echo ""

# Função para filtrar logs da IA
filter_ai_logs() {
    docker service logs -f cidadaoai_cidadaoai_app 2>&1 | \
    grep -E "(🤖|Agente|IA|OpenAI|message_created|incoming|Contact|DEBUG.*sender_type|Condições|processando.*mensagem)" | \
    while IFS= read -r line; do
        # Extrair timestamp e mensagem
        timestamp=$(echo "$line" | sed -n 's/.*\([0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}T[0-9]\{2\}:[0-9]\{2\}:[0-9]\{2\}\)\.\([0-9]\{6\}\).*/\1/p')
        message=$(echo "$line" | sed 's/.*INFO:__main__://' | sed 's/.*INFO:backend\.ai_agent://' | sed 's/.*INFO:backend\.//')
        
        # Colorir diferentes tipos de log
        if echo "$line" | grep -q "🤖"; then
            echo -e "\033[35m🤖 $message\033[0m"  # Roxo para IA
        elif echo "$line" | grep -q "DEBUG.*sender_type"; then
            echo -e "\033[33m🔍 $message\033[0m"  # Amarelo para debug
        elif echo "$line" | grep -q "Condições"; then
            echo -e "\033[36m⚡ $message\033[0m"  # Ciano para condições
        elif echo "$line" | grep -q "incoming.*Contact"; then
            echo -e "\033[32m✅ $message\033[0m"  # Verde para sucesso
        elif echo "$line" | grep -q "message_created"; then
            echo -e "\033[34m📨 $message\033[0m"  # Azul para mensagens
        else
            echo -e "\033[37mℹ️  $message\033[0m"  # Branco para outros
        fi
    done
}

# Executar o filtro
filter_ai_logs
