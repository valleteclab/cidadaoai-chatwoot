# 🔧 Cidadão.AI - Guia de Troubleshooting

## 🚨 Problemas Críticos

### ❌ **Serviço não inicia**

**Sintomas:**
- `docker service ps cidadaoai_app` mostra erro
- Logs mostram `Exit code: 1`

**Diagnóstico:**
```bash
# Ver logs detalhados
docker service logs cidadaoai_app

# Verificar sintaxe Python
python -m py_compile backend/main.py
python -m py_compile backend/chamados_service.py
python -m py_compile backend/models.py
```

**Soluções:**
```bash
# 1. Verificar imports
cd /root/projetos/cidadaoai-chatwoot
source venv/bin/activate
python -c "import backend.main"

# 2. Verificar dependências
pip list | grep -E "(fastapi|asyncpg|pydantic)"

# 3. Reiniciar serviço
docker service update --force cidadaoai_app

# 4. Recriar serviço (último recurso)
docker service rm cidadaoai_app
docker stack deploy -c docker-compose.yml cidadaoai
```

---

### ❌ **Banco de dados não conecta**

**Sintomas:**
- Logs mostram: `[Errno -2] Name or service not known`
- `database_connected: false` no status

**Diagnóstico:**
```bash
# 1. Verificar PostgreSQL
docker ps | grep postgres

# 2. Testar conexão
PGPASSWORD="cidadaoai_senha_2024" psql -h 212.85.0.166 -p 5433 -U cidadaoai_user -d cidadaoai -c "SELECT 1;"

# 3. Verificar DATABASE_URL
cat .env | grep DATABASE_URL

# 4. Verificar rede
docker network ls
docker network inspect LomeServer
```

**Soluções:**
```bash
# 1. Corrigir DATABASE_URL no .env
DATABASE_URL=postgresql://cidadaoai_user:cidadaoai_senha_2024@212.85.0.166:5433/cidadaoai

# 2. Reiniciar PostgreSQL
docker restart cidadaoai_postgres

# 3. Verificar firewall
netstat -tlnp | grep 5433

# 4. Testar conectividade
telnet 212.85.0.166 5433
```

---

### ❌ **IA não responde**

**Sintomas:**
- Cidadão não recebe resposta automática
- `chamados_ai_available: false`

**Diagnóstico:**
```bash
# 1. Verificar API key
echo $GROQ_API_KEY

# 2. Testar endpoint
curl https://tecnico.sisgov.app.br/api/chamados/status

# 3. Verificar logs da IA
docker service logs cidadaoai_app | grep -i "groq\|ai\|agent"

# 4. Testar API externa
curl -X POST "https://api.groq.com/openai/v1/chat/completions" \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": "test"}]}'
```

**Soluções:**
```bash
# 1. Exportar API key
export GROQ_API_KEY="SUA_CHAVE_GROQ_AQUI"

# 2. Redeploy com nova key
docker service update --env-add GROQ_API_KEY=$GROQ_API_KEY cidadaoai_app

# 3. Verificar quota da API
# Acessar: https://console.groq.com/usage
```

---

## ⚠️ Problemas Moderados

### ⚠️ **Frontend não carrega**

**Sintomas:**
- 404 Not Found no `/admin`
- Arquivos não encontrados

**Diagnóstico:**
```bash
# 1. Verificar arquivos
ls -la frontend/admin/index.html

# 2. Verificar permissões
chmod 644 frontend/admin/index.html

# 3. Testar endpoint
curl https://tecnico.sisgov.app.br/admin
```

**Soluções:**
```bash
# 1. Recriar arquivo
touch frontend/admin/index.html
chmod 644 frontend/admin/index.html

# 2. Verificar rota no main.py
grep -n "admin" backend/main.py

# 3. Reiniciar serviço
docker service update --force cidadaoai_app
```

---

### ⚠️ **Erro de validação Pydantic**

**Sintomas:**
- `1 validation error for Cidadao config`
- Cadastro falha mas dados são salvos

**Diagnóstico:**
```bash
# 1. Verificar logs específicos
docker service logs cidadaoai_app | grep -i "validation\|pydantic"

# 2. Verificar estrutura do banco
PGPASSWORD="cidadaoai_senha_2024" psql -h 212.85.0.166 -p 5433 -U cidadaoai_user -d cidadaoai -c "\d cidadaos"

# 3. Verificar dados problemáticos
PGPASSWORD="cidadaoai_senha_2024" psql -h 212.85.0.166 -p 5433 -U cidadaoai_user -d cidadaoai -c "SELECT id, config FROM cidadaos LIMIT 5;"
```

**Soluções:**
```bash
# 1. Atualizar código (já implementado)
git pull origin main
./update-server.sh

# 2. Limpar dados problemáticos
PGPASSWORD="cidadaoai_senha_2024" psql -h 212.85.0.166 -p 5433 -U cidadaoai_user -d cidadaoai -c "UPDATE cidadaos SET config = '{}' WHERE config IS NULL;"
```

---

### ⚠️ **Webhook não funciona**

**Sintomas:**
- Mensagens do WhatsApp não chegam
- Chatwoot não envia webhooks

**Diagnóstico:**
```bash
# 1. Verificar webhook no Chatwoot
# Acessar: https://chat.sisgov.app.br/app/accounts/1/settings/integrations

# 2. Verificar logs do webhook
docker service logs cidadaoai_app | grep -i "webhook"

# 3. Testar endpoint manualmente
curl -X POST https://tecnico.sisgov.app.br/webhook/chatwoot \
  -H "Content-Type: application/json" \
  -d '{"event": "message_created", "data": {"id": 1}}'
```

**Soluções:**
```bash
# 1. Reconfigurar webhook no Chatwoot
# URL: https://tecnico.sisgov.app.br/webhook/chatwoot
# Eventos: message_created, conversation_updated

# 2. Verificar SSL
curl -I https://tecnico.sisgov.app.br/webhook/chatwoot

# 3. Testar localmente
curl -X POST http://localhost:8000/webhook/chatwoot \
  -H "Content-Type: application/json" \
  -d '{"event": "test"}'
```

---

## 🔍 Comandos de Diagnóstico

### 📊 **Status Completo do Sistema**

```bash
#!/bin/bash
echo "=== STATUS DO SISTEMA CIDADÃO.AI ==="
echo ""

echo "1. Serviços Docker:"
docker service ls | grep cidadaoai

echo ""
echo "2. Containers Ativos:"
docker ps | grep -E "(cidadaoai|postgres)"

echo ""
echo "3. Status da API:"
curl -s https://tecnico.sisgov.app.br/api/chamados/status | jq '.'

echo ""
echo "4. Métricas do Sistema:"
curl -s https://tecnico.sisgov.app.br/api/chamados/metrics | jq '.metrics'

echo ""
echo "5. Últimos Logs:"
docker service logs --tail 10 cidadaoai_app

echo ""
echo "6. Conectividade do Banco:"
PGPASSWORD="cidadaoai_senha_2024" psql -h 212.85.0.166 -p 5433 -U cidadaoai_user -d cidadaoai -c "SELECT COUNT(*) as total_cidadaos FROM cidadaos;" 2>/dev/null || echo "❌ Erro de conexão"

echo ""
echo "7. Espaço em Disco:"
df -h | grep -E "(/$|/root)"

echo ""
echo "=== FIM DO DIAGNÓSTICO ==="
```

### 🔧 **Script de Recuperação**

```bash
#!/bin/bash
echo "=== SCRIPT DE RECUPERAÇÃO CIDADÃO.AI ==="

# 1. Backup do banco
echo "1. Fazendo backup do banco..."
PGPASSWORD="cidadaoai_senha_2024" pg_dump -h 212.85.0.166 -p 5433 -U cidadaoai_user cidadaoai > backup_recovery_$(date +%Y%m%d_%H%M%S).sql

# 2. Parar serviços
echo "2. Parando serviços..."
docker service rm cidadaoai_app 2>/dev/null

# 3. Atualizar código
echo "3. Atualizando código..."
cd /root/projetos/cidadaoai-chatwoot
git pull origin main

# 4. Recriar serviço
echo "4. Recriando serviço..."
docker stack deploy -c docker-compose.yml cidadaoai

# 5. Aguardar inicialização
echo "5. Aguardando inicialização..."
sleep 30

# 6. Verificar status
echo "6. Verificando status..."
curl -s https://tecnico.sisgov.app.br/api/chamados/status | jq '.'

echo "=== RECUPERAÇÃO CONCLUÍDA ==="
```

---

## 📋 Checklist de Verificação

### ✅ **Verificação Diária**

- [ ] Serviço está rodando: `docker service ps cidadaoai_app`
- [ ] API responde: `curl https://tecnico.sisgov.app.br/api/chamados/status`
- [ ] Banco conecta: `PGPASSWORD="..." psql -h ... -c "SELECT 1;"`
- [ ] Frontend carrega: https://tecnico.sisgov.app.br/admin
- [ ] Logs sem erros: `docker service logs --tail 20 cidadaoai_app`

### ✅ **Verificação Semanal**

- [ ] Backup do banco
- [ ] Espaço em disco: `df -h`
- [ ] Logs de erro: `docker service logs cidadaoai_app | grep -i error`
- [ ] Métricas do sistema: https://tecnico.sisgov.app.br/api/chamados/metrics
- [ ] Teste completo via WhatsApp

### ✅ **Verificação Mensal**

- [ ] Atualização de dependências
- [ ] Limpeza de logs antigos
- [ ] Verificação de segurança
- [ ] Performance do sistema
- [ ] Backup completo

---

## 🆘 Contatos de Emergência

### 📞 **Em caso de falha crítica:**

1. **Verificar logs** primeiro
2. **Executar script de diagnóstico**
3. **Fazer backup** antes de qualquer alteração
4. **Documentar** o problema e solução

### 🔗 **Links Úteis:**

- **Servidor:** ssh root@212.85.0.166
- **Dashboard:** https://tecnico.sisgov.app.br/
- **Admin:** https://tecnico.sisgov.app.br/admin
- **API Docs:** https://tecnico.sisgov.app.br/docs
- **Groq Console:** https://console.groq.com/
- **Chatwoot:** https://chat.sisgov.app.br/

---

**📅 Última atualização:** 29 de Dezembro de 2024  
**🔧 Versão do guia:** 1.0.0
