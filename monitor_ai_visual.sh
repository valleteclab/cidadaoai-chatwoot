#!/bin/bash

# Script de monitoramento visual da IA em tempo real
# Uso: ./monitor_ai_visual.sh

echo "🤖 MONITOR VISUAL DA IA - Cidadão.AI"
echo "===================================="
echo "Pressione Ctrl+C para sair"
echo ""

# Função para mostrar status atual
show_status() {
    echo ""
    echo "📊 STATUS ATUAL:"
    echo "================"
    
    # Verificar status via API
    response=$(curl -s https://tecnico.sisgov.app.br/api/agent/status 2>/dev/null)
    
    if echo "$response" | grep -q '"agent_available":true'; then
        echo "✅ Agente: DISPONÍVEL"
        
        # Extrair provedor atual
        provider=$(echo "$response" | grep -o '"current_provider":"[^"]*"' | cut -d'"' -f4)
        echo "🔧 Provedor: $provider"
        
        # Extrair conversas em memória
        memory=$(echo "$response" | grep -o '"conversation_memory_count":[0-9]*' | cut -d':' -f2)
        echo "💬 Conversas em memória: $memory"
        
    else
        echo "❌ Agente: INDISPONÍVEL"
    fi
    
    echo ""
}

# Função para monitorar logs da IA
monitor_logs() {
    echo "🔍 MONITORANDO LOGS DA IA..."
    echo "============================="
    
    docker service logs -f cidadaoai_cidadaoai_app 2>&1 | \
    grep -E "(🤖|🚀|📥|🚨|ERRO|INÍCIO|ENVIANDO|RESPOSTA|Provedor|provider)" | \
    while IFS= read -r line; do
        timestamp=$(date '+%H:%M:%S')
        
        # Colorir diferentes tipos de log
        if echo "$line" | grep -q "🤖 INÍCIO"; then
            echo -e "\033[32m[$timestamp] 🟢 $line\033[0m"
        elif echo "$line" | grep -q "🚀 ENVIANDO"; then
            echo -e "\033[34m[$timestamp] 🔵 $line\033[0m"
        elif echo "$line" | grep -q "📥 RESPOSTA"; then
            echo -e "\033[35m[$timestamp] 🟣 $line\033[0m"
        elif echo "$line" | grep -q "🚨 ERRO"; then
            echo -e "\033[31m[$timestamp] 🔴 $line\033[0m"
        elif echo "$line" | grep -q "Provedor"; then
            echo -e "\033[33m[$timestamp] 🟡 $line\033[0m"
        else
            echo -e "\033[37m[$timestamp] ⚪ $line\033[0m"
        fi
    done
}

# Função para testar IA
test_ai() {
    echo ""
    echo "🧪 TESTANDO IA..."
    echo "=================="
    
    response=$(curl -s -X POST https://tecnico.sisgov.app.br/api/agent/test \
      -H "Content-Type: application/json" \
      -d '{
        "message": "Olá, como posso pagar meu IPTU?",
        "conversation_id": 999,
        "contact_info": {
          "id": 7,
          "name": "teste",
          "phone_number": "+557798755764"
        }
      }')
    
    if echo "$response" | grep -q '"status":"success"'; then
        ai_response=$(echo "$response" | grep -o '"ai_response":"[^"]*"' | cut -d'"' -f4)
        echo "✅ Teste realizado"
        echo "📝 Resposta: $ai_response"
        
        if echo "$ai_response" | grep -q "🚨 ERRO"; then
            echo "❌ IA usando fallback!"
        else
            echo "✅ IA funcionando corretamente!"
        fi
    else
        echo "❌ Erro no teste: $response"
    fi
    echo ""
}

# Mostrar status inicial
show_status

# Loop principal
while true; do
    echo "Opções:"
    echo "1) Monitorar logs em tempo real"
    echo "2) Testar IA"
    echo "3) Verificar status"
    echo "4) Sair"
    echo ""
    read -p "Escolha uma opção (1-4): " choice
    
    case $choice in
        1)
            monitor_logs
            ;;
        2)
            test_ai
            ;;
        3)
            show_status
            ;;
        4)
            echo "Saindo..."
            exit 0
            ;;
        *)
            echo "Opção inválida"
            ;;
    esac
done
