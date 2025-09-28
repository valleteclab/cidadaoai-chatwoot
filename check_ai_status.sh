#!/bin/bash

# Script simples para verificar status da IA
# Uso: ./check_ai_status.sh

echo "🤖 Status da IA - Cidadão.AI"
echo "============================="

# Verificar se o serviço está rodando
echo "📡 Verificando serviço Docker..."
if docker service ls --filter name=cidadaoai | grep -q "cidadaoai_cidadaoai_app"; then
    echo "✅ Serviço Docker está rodando"
else
    echo "❌ Serviço Docker não está rodando"
    exit 1
fi

echo ""

# Verificar status da IA via API
echo "🔍 Verificando status da IA..."
response=$(curl -s https://tecnico.sisgov.app.br/api/agent/status)

if echo "$response" | grep -q '"agent_available":true'; then
    echo "✅ Agente IA está disponível"
    
    # Extrair informações específicas
    memory_count=$(echo "$response" | grep -o '"conversation_memory_count":[0-9]*' | cut -d':' -f2)
    echo "📊 Conversas em memória: $memory_count"
    
    if echo "$response" | grep -q '"openai_configured":true'; then
        echo "🔑 Chave OpenAI configurada"
    else
        echo "❌ Chave OpenAI não configurada"
    fi
else
    echo "❌ Agente IA não está disponível"
    echo "Resposta: $response"
fi

echo ""

# Verificar debug info
echo "🐛 Informações de Debug..."
debug_response=$(curl -s https://tecnico.sisgov.app.br/api/agent/debug)

if echo "$debug_response" | grep -q '"status":"success"'; then
    echo "✅ Debug info disponível"
    
    # Mostrar conversas ativas
    conversations=$(echo "$debug_response" | grep -o '"conversation_ids":\[.*\]' | sed 's/"conversation_ids":\[//' | sed 's/\]//')
    if [ "$conversations" != "null" ] && [ "$conversations" != "" ]; then
        echo "💬 Conversas ativas: $conversations"
    else
        echo "💬 Nenhuma conversa ativa"
    fi
else
    echo "❌ Erro ao obter debug info"
fi

echo ""
echo "🕐 $(date)"
