# 🚀 Cidadão.AI - Comandos Rápidos

## 🌐 Acesso ao Servidor

```bash
# SSH
ssh root@212.85.0.166

# Navegar para projeto
cd /root/projetos/cidadaoai-chatwoot

# Ativar ambiente virtual
source venv/bin/activate
```

## 📦 Git e Deploy

```bash
# Status
git status

# Add e commit
git add .
git commit -m "Descrição"
git push origin main

# Pull no servidor
git pull origin main

# Deploy
./update-server.sh
```

## 🔍 Monitoramento

```bash
# Logs do serviço
docker service logs cidadaoai_app

# Logs em tempo real
docker service logs -f cidadaoai_app

# Status do serviço
docker service ps cidadaoai_app

# Containers ativos
docker ps
```

## 🗄️ Banco de Dados

```bash
# Conectar
PGPASSWORD="cidadaoai_senha_2024" psql -h 212.85.0.166 -p 5433 -U cidadaoai_user -d cidadaoai

# Ver cidadãos
SELECT id, nome, telefone, email, created_at FROM cidadaos ORDER BY created_at DESC LIMIT 10;

# Ver chamados
SELECT id, protocolo, titulo, status, created_at FROM chamados ORDER BY created_at DESC LIMIT 10;

# Contar registros
SELECT COUNT(*) FROM cidadaos WHERE active = true;
SELECT COUNT(*) FROM chamados;
```

## 🌐 URLs Importantes

- **Dashboard Técnico:** https://tecnico.sisgov.app.br/
- **Painel Admin:** https://tecnico.sisgov.app.br/admin
- **API Docs:** https://tecnico.sisgov.app.br/docs
- **Status API:** https://tecnico.sisgov.app.br/api/chamados/status

## 🔧 Troubleshooting

```bash
# Reiniciar serviço
docker service update --force cidadaoai_app

# Verificar .env
cat .env

# Testar conexão DB
PGPASSWORD="cidadaoai_senha_2024" psql -h 212.85.0.166 -p 5433 -U cidadaoai_user -d cidadaoai -c "SELECT 1;"

# Verificar API
curl https://tecnico.sisgov.app.br/api/chamados/status

# Backup do banco
PGPASSWORD="cidadaoai_senha_2024" pg_dump -h 212.85.0.166 -p 5433 -U cidadaoai_user cidadaoai > backup_$(date +%Y%m%d_%H%M%S).sql
```

## 📱 Teste WhatsApp

1. Envie mensagem para o WhatsApp da prefeitura
2. Verifique logs: `docker service logs -f cidadaoai_app`
3. Verifique no admin: https://tecnico.sisgov.app.br/admin
4. Consulte banco: `SELECT * FROM cidadaos ORDER BY created_at DESC LIMIT 5;`
