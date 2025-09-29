# 🏛️ Cidadão.AI - Sistema de Chamados para Prefeituras
## Manual Completo de Implementação e Operação

---

## 📋 Índice

1. [Visão Geral do Sistema](#visão-geral)
2. [Arquitetura Implementada](#arquitetura)
3. [Funcionalidades da Fase 1](#funcionalidades-fase1)
4. [Comandos de Operação](#comandos-operacao)
5. [Troubleshooting](#troubleshooting)
6. [Próximas Fases](#proximas-fases)
7. [APIs e Endpoints](#apis-endpoints)
8. [Banco de Dados](#banco-dados)

---

## 🎯 Visão Geral do Sistema {#visão-geral}

O **Cidadão.AI** é um sistema completo de atendimento ao cidadão via WhatsApp, integrado com Chatwoot, que permite:

- **Cadastro automático de cidadãos** via IA
- **Categorização inteligente** de chamados
- **Geração automática de protocolos** únicos
- **Gestão completa** via interface web
- **Relatórios e métricas** em tempo real

### 🏗️ Stack Tecnológica

- **Backend:** FastAPI + Python 3.12
- **Banco:** PostgreSQL + asyncpg
- **IA:** Groq API (Llama 3.1)
- **Frontend:** HTML + Tailwind CSS + Alpine.js
- **Deploy:** Docker Swarm + Nginx + Traefik
- **Monitoramento:** WebSocket + Logs estruturados

---

## 🏛️ Arquitetura Implementada {#arquitetura}

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   WhatsApp      │    │    Chatwoot     │    │   Cidadão.AI    │
│   Business API  │◄──►│   (Frontend)    │◄──►│   (Backend)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │   PostgreSQL    │
                                               │   (Database)    │
                                               └─────────────────┘
```

### 🔄 Fluxo de Atendimento

1. **Cidadão envia mensagem** via WhatsApp
2. **Chatwoot recebe** e envia webhook para Cidadão.AI
3. **IA analisa** a mensagem e determina ação:
   - Se é cadastro → coleta dados automaticamente
   - Se é chamado → categoriza e gera protocolo
   - Se é consulta → busca status do chamado
4. **Sistema responde** automaticamente via Chatwoot
5. **Dados são armazenados** no PostgreSQL

---

## ✅ Funcionalidades da Fase 1 {#funcionalidades-fase1}

### 🤖 Sistema de IA Especializado

- **Cadastro Automático:** IA coleta dados do cidadão (nome, telefone, email, endereço)
- **Categorização Inteligente:** Classifica chamados por secretaria (Infraestrutura, Saúde, Educação, etc.)
- **Geração de Protocolos:** Formato `CATEGORIA-YYYY-NNN` (ex: INFRA-2024-001)
- **Memória de Conversas:** IA lembra interações anteriores
- **Confirmação de Categoria:** Sempre confirma com o cidadão antes de finalizar

### 📊 Dashboard Administrativo

- **Métricas em Tempo Real:**
  - Total de cidadãos cadastrados
  - Total de chamados
  - Chamados em andamento
  - Chamados resolvidos

- **Gestão de Dados:**
  - Lista completa de cidadãos
  - Lista completa de chamados
  - Status do sistema (banco + IA)

### 🔧 Sistema de Categorias

Categorias pré-configuradas com SLA automático:

| Categoria | SLA | Prioridade | Time Responsável |
|-----------|-----|------------|------------------|
| Infraestrutura | 24h | Alta | Secretaria de Obras |
| Saúde | 4h | Crítica | Secretaria de Saúde |
| Educação | 48h | Média | Secretaria de Educação |
| Assistência Social | 72h | Média | Secretaria de Assistência |
| Limpeza Urbana | 24h | Alta | Secretaria de Serviços |

---

## 🚀 Comandos de Operação {#comandos-operacao}

### 🌐 Acesso ao Servidor

```bash
# SSH para o servidor
ssh root@212.85.0.166

# Navegar para o projeto
cd /root/projetos/cidadaoai-chatwoot

# Ativar ambiente virtual
source venv/bin/activate
```

### 📦 Git e Deploy

```bash
# Verificar status
git status

# Adicionar arquivos
git add .

# Commit
git commit -m "Descrição da alteração"

# Push para repositório
git push origin main

# Pull no servidor
git pull origin main

# Deploy no servidor
./update-server.sh
```

### 🔍 Monitoramento

```bash
# Ver logs do serviço
docker service logs cidadaoai_app

# Ver logs em tempo real
docker service logs -f cidadaoai_app

# Ver status do serviço
docker service ps cidadaoai_app

# Verificar containers
docker ps

# Verificar redes
docker network ls
```

### 🗄️ Banco de Dados

```bash
# Conectar ao PostgreSQL
PGPASSWORD="cidadaoai_senha_2024" psql -h 212.85.0.166 -p 5433 -U cidadaoai_user -d cidadaoai

# Ver cidadãos cadastrados
SELECT id, nome, telefone, email, created_at FROM cidadaos ORDER BY created_at DESC LIMIT 10;

# Ver chamados
SELECT id, protocolo, titulo, status, created_at FROM chamados ORDER BY created_at DESC LIMIT 10;

# Ver métricas
SELECT 
    COUNT(*) as total_cidadaos 
FROM cidadaos WHERE active = true;

SELECT 
    COUNT(*) as total_chamados,
    COUNT(CASE WHEN status = 'em_andamento' THEN 1 END) as em_andamento,
    COUNT(CASE WHEN status = 'resolvido' THEN 1 END) as resolvidos
FROM chamados;
```

---

## 🔧 Troubleshooting {#troubleshooting}

### ❌ Problemas Comuns e Soluções

#### 1. **Serviço não inicia**

```bash
# Verificar logs
docker service logs cidadaoai_app

# Verificar se há erros de sintaxe
python -m py_compile backend/main.py

# Reiniciar serviço
docker service update --force cidadaoai_app
```

#### 2. **Banco de dados não conecta**

```bash
# Verificar se PostgreSQL está rodando
docker ps | grep postgres

# Testar conexão
PGPASSWORD="cidadaoai_senha_2024" psql -h 212.85.0.166 -p 5433 -U cidadaoai_user -d cidadaoai -c "SELECT 1;"

# Verificar DATABASE_URL no .env
cat .env | grep DATABASE_URL
```

#### 3. **IA não responde**

```bash
# Verificar API key
echo $GROQ_API_KEY

# Testar endpoint de status
curl https://tecnico.sisgov.app.br/api/chamados/status

# Verificar logs da IA
docker service logs cidadaoai_app | grep -i "groq\|ai\|agent"
```

#### 4. **Frontend não carrega**

```bash
# Verificar se arquivos existem
ls -la frontend/admin/index.html

# Verificar permissões
chmod 644 frontend/admin/index.html

# Testar endpoint
curl https://tecnico.sisgov.app.br/admin
```

#### 5. **Erro de validação Pydantic**

```bash
# Verificar logs específicos
docker service logs cidadaoai_app | grep -i "validation\|pydantic"

# Verificar estrutura do banco
PGPASSWORD="cidadaoai_senha_2024" psql -h 212.85.0.166 -p 5433 -U cidadaoai_user -d cidadaoai -c "\d cidadaos"
```

### 🔄 Comandos de Recuperação

```bash
# Recriar serviço completamente
docker service rm cidadaoai_app
docker stack deploy -c docker-compose.yml cidadaoai

# Resetar banco (CUIDADO!)
PGPASSWORD="cidadaoai_senha_2024" psql -h 212.85.0.166 -p 5433 -U cidadaoai_user -d cidadaoai -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
./apply_migration.sh

# Backup do banco
PGPASSWORD="cidadaoai_senha_2024" pg_dump -h 212.85.0.166 -p 5433 -U cidadaoai_user cidadaoai > backup_$(date +%Y%m%d_%H%M%S).sql
```

---

## 🚀 Próximas Fases {#proximas-fases}

### 📅 Fase 2 - Interface de Gestão (Q1 2025)

- [ ] **Dashboard Avançado** com gráficos e analytics
- [ ] **Editor de Templates** para respostas da IA
- [ ] **Gestão de Times** e agentes humanos
- [ ] **Sistema de Notificações** automáticas
- [ ] **Relatórios Personalizados** por secretaria

### 📅 Fase 3 - Multi-Prefeitura (Q2 2025)

- [ ] **Suporte Multi-Tenant** para múltiplas prefeituras
- [ ] **Configurações por Prefeitura** (categorias, SLA, etc.)
- [ ] **API Pública** para integração com sistemas externos
- [ ] **App Mobile** para gestores
- [ ] **Sistema de Permissões** granular

### 📅 Fase 4 - Automações Avançadas (Q3 2025)

- [ ] **Workflows Automatizados** (n8n/Dify)
- [ ] **Integração com Sistemas** externos (ERP, SIG)
- [ ] **Chatbot Especializado** por secretaria
- [ ] **Análise de Sentimento** das mensagens
- [ ] **Predição de Demanda** por categoria

---

## 🔌 APIs e Endpoints {#apis-endpoints}

### 📡 Endpoints Principais

#### **Sistema de Chamados**

```bash
# Status do sistema
GET /api/chamados/status
Response: {
  "database_connected": true,
  "chamados_ai_available": true,
  "timestamp": "2025-01-01T12:00:00Z"
}

# Métricas do dashboard
GET /api/chamados/metrics
Response: {
  "status": "success",
  "metrics": {
    "total_cidadaos": 150,
    "total_chamados": 45,
    "chamados_em_andamento": 12,
    "chamados_resolvidos": 33
  }
}

# Listar cidadãos
GET /api/chamados/cidadaos
Response: {
  "status": "success",
  "data": [...],
  "total": 150
}

# Listar chamados
GET /api/chamados/chamados
Response: {
  "status": "success", 
  "data": [...],
  "total": 45
}

# Criar chamado
POST /api/chamados/criar
Body: {
  "titulo": "Buraco na rua",
  "descricao": "Descrição detalhada",
  "endereco_ocorrencia": "Rua X, 123",
  "fonte": "whatsapp"
}

# Consultar chamado
POST /api/chamados/consultar
Body: {
  "protocolo": "INFRA-2024-001"
}
```

#### **Frontend**

```bash
# Dashboard técnico (tempo real)
GET https://tecnico.sisgov.app.br/

# Painel administrativo
GET https://tecnico.sisgov.app.br/admin

# Documentação da API
GET https://tecnico.sisgov.app.br/docs
```

---

## 🗄️ Banco de Dados {#banco-dados}

### 📋 Schema Principal

#### **Tabelas Implementadas**

```sql
-- Prefeituras (multi-tenant)
prefeituras (id, nome, config, active, created_at, updated_at)

-- Times/Secretarias
times (id, prefeitura_id, nome, config, active, created_at, updated_at)

-- Agentes (IA + Humanos)
agentes (id, prefeitura_id, nome, tipo, config, active, created_at, updated_at)

-- Relação Agente-Time
agente_times (agente_id, time_id, created_at)

-- Cidadãos
cidadaos (id, prefeitura_id, nome, cpf, telefone, email, endereco, ...)

-- Categorias de Chamados
categorias_chamados (id, prefeitura_id, nome, sla_horas, prioridade, time_id, ...)

-- Chamados
chamados (id, prefeitura_id, protocolo, cidadao_id, categoria_id, titulo, ...)

-- Interações dos Chamados
interacoes_chamado (id, chamado_id, agente_id, tipo, conteudo, ...)

-- Templates de Resposta
templates_resposta (id, prefeitura_id, nome, conteudo, categoria_id, ...)

-- Configurações de IA
config_ia (id, prefeitura_id, nome, provider, config, active, ...)
```

### 🔍 Consultas Úteis

```sql
-- Top 10 cidadãos mais ativos
SELECT c.nome, c.telefone, COUNT(ch.id) as total_chamados
FROM cidadaos c
LEFT JOIN chamados ch ON c.id = ch.cidadao_id
GROUP BY c.id, c.nome, c.telefone
ORDER BY total_chamados DESC
LIMIT 10;

-- Chamados por categoria este mês
SELECT cat.nome, COUNT(*) as total
FROM chamados ch
JOIN categorias_chamados cat ON ch.categoria_id = cat.id
WHERE ch.created_at >= date_trunc('month', CURRENT_DATE)
GROUP BY cat.nome
ORDER BY total DESC;

-- Tempo médio de resolução por categoria
SELECT cat.nome, 
       AVG(EXTRACT(EPOCH FROM (ch.resolved_at - ch.created_at))/3600) as horas_media
FROM chamados ch
JOIN categorias_chamados cat ON ch.categoria_id = cat.id
WHERE ch.status = 'resolvido' AND ch.resolved_at IS NOT NULL
GROUP BY cat.nome;
```

---

## 📞 Suporte e Contato

### 🆘 Em caso de problemas:

1. **Verifique os logs** primeiro
2. **Consulte este manual** de troubleshooting
3. **Execute os comandos** de diagnóstico
4. **Faça backup** antes de mudanças críticas

### 📧 Informações do Sistema

- **Servidor:** 212.85.0.166
- **Domínio:** tecnico.sisgov.app.br
- **Repositório:** https://github.com/valleteclab/cidadaoai-chatwoot
- **Documentação:** docs/MANUAL_COMPLETO_SISTEMA.md

---

## 🎯 Resumo do Status Atual

### ✅ **Implementado e Funcionando:**
- Sistema completo de cadastro de cidadãos
- IA especializada para atendimento
- Geração automática de protocolos
- Categorização inteligente de chamados
- Dashboard administrativo
- APIs completas
- Banco de dados estruturado
- Deploy automatizado

### 🔄 **Em Teste:**
- Validação de cadastro via WhatsApp
- Interface administrativa
- Métricas em tempo real

### 📋 **Próximos Passos:**
1. Finalizar testes da Fase 1
2. Implementar Fase 2 (Interface de Gestão)
3. Adicionar relatórios avançados
4. Preparar para multi-prefeitura

---

**📅 Última atualização:** 29 de Dezembro de 2024  
**👨‍💻 Desenvolvido por:** Equipe Cidadão.AI  
**🏛️ Versão:** 1.0.0 (Fase 1)
