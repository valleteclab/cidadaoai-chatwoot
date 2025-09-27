#!/bin/bash

echo "🔍 Diagnosticando Chatwoot Self-Hosted"
echo "======================================"

# 1. Verificar se o Chatwoot está rodando
echo "1. Status do serviço Chatwoot:"
sudo systemctl status chatwoot --no-pager -l

echo -e "\n2. Verificando porta 3000:"
sudo netstat -tlnp | grep :3000

echo -e "\n3. Testando resposta do servidor:"
curl -I https://chat.sisgov.app.br 2>/dev/null || echo "❌ Servidor não responde"

echo -e "\n4. Verificando Nginx:"
sudo systemctl status nginx --no-pager -l

echo -e "\n5. Testando configuração do Nginx:"
sudo nginx -t 2>&1

echo -e "\n6. Verificando DNS:"
nslookup chat.sisgov.app.br 2>/dev/null || echo "❌ DNS não resolve"

echo -e "\n7. Verificando se o Chatwoot está acessível localmente:"
curl -I http://localhost:3000 2>/dev/null || echo "❌ Chatwoot não está rodando localmente"

echo -e "\n8. Verificando logs recentes do Chatwoot:"
sudo journalctl -u chatwoot --no-pager -l -n 10

echo -e "\n9. Verificando processos do Chatwoot:"
ps aux | grep -i chatwoot | grep -v grep

echo -e "\n10. Verificando configuração do Chatwoot:"
if [ -f /home/chatwoot/chatwoot/.env ]; then
    echo "✅ Arquivo .env encontrado"
    echo "Configurações relevantes:"
    grep -E "(FRONTEND_URL|FORCE_SSL|RAILS_ENV)" /home/chatwoot/chatwoot/.env 2>/dev/null || echo "❌ Configurações não encontradas"
else
    echo "❌ Arquivo .env não encontrado"
fi

echo -e "\n======================================"
echo "📊 Resumo do diagnóstico concluído"
