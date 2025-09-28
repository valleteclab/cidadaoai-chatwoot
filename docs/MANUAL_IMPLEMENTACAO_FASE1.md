# 📋 MANUAL DE IMPLEMENTAÇÃO - FASE 1
## Sistema de Chamados Cidadãos

**Data:** 28 de Dezembro de 2024  
**Versão:** 1.0  
**Status:** Implementado ✅

---

## 🎯 OBJETIVOS DA FASE 1

- ✅ Criar estrutura completa do banco de dados
- ✅ Implementar sistema de cadastro de cidadãos
- ✅ Implementar geração automática de protocolos
- ✅ Implementar categorização automática de chamados
- ✅ Integrar com sistema de IA existente
- ✅ Criar endpoints de API para gestão

---

## 📁 ARQUIVOS CRIADOS/MODIFICADOS

### **Novos Arquivos:**
```
backend/migrations/001_create_chamados_system.sql  # Schema do banco
backend/chamados_service.py                        # Serviço principal
backend/chamados_ai_service.py                     # IA especializada
apply_migration.sh                                 # Script de migration
docs/database_schema.sql                           # Schema detalhado
docs/fluxo_sistema.md                             # Fluxo do sistema
docs/MANUAL_IMPLEMENTACAO_FASE1.md               # Este manual
```

### **Arquivos Modificados:**
```
backend/models.py          # Novos modelos Pydantic
backend/main.py            # Integração e endpoints
requirements.txt           # Nova dependência asyncpg
```

---

## 🗄️ ESTRUTURA DO BANCO DE DADOS

### **Tabelas Principais:**

1. **`prefeituras`** - Clientes/Prefeituras
2. **`times`** - Secretarias/Departamentos  
3. **`agentes`** - Agentes humanos e IA
4. **`agente_times`** - Relacionamento agente-time
5. **`cidadaos`** - Cidadãos cadastrados
6. **`categorias_chamados`** - Categorias de problemas
7. **`chamados`** - Protocolos/Chamados
8. **`interacoes_chamado`** - Histórico de interações
9. **`templates_resposta`** - Templates de resposta
10. **`config_ia`** - Configurações de IA

### **Views Criadas:**
- **`vw_relatorio_chamados`** - Relatórios de chamados
- **`vw_dashboard_metrics`** - Métricas para dashboard

### **Funções Criadas:**
- **`gerar_protocolo_chamado()`** - Gera protocolos únicos
- **`update_updated_at_column()`** - Atualiza timestamps

---

## 🤖 FLUXO DO SISTEMA DE IA

### **Estados da Conversa:**
1. **`initial`** - Primeira mensagem
2. **`collecting_data`** - Coletando dados do cidadão
3. **`collecting_issue`** - Coletando descrição do problema
4. **`confirming_category`** - Confirmando categoria sugerida
5. **`collecting_address`** - Coletando endereço do problema
6. **`ticket_created`** - Chamado criado

### **Processo Completo:**
```
Cidadão envia mensagem
    ↓
IA detecta: primeira mensagem?
    ↓
IA coleta: Nome → CPF → Endereço → Email
    ↓
IA cadastra cidadão no banco
    ↓
IA coleta descrição do problema
    ↓
IA categoriza automaticamente
    ↓
IA confirma categoria com cidadão
    ↓
IA coleta endereço do problema
    ↓
IA cria chamado com protocolo único
    ↓
IA informa protocolo ao cidadão
```

---

## 🔗 ENDPOINTS IMPLEMENTADOS

### **Status e Monitoramento:**
- `GET /api/chamados/status` - Status do sistema
- `GET /api/chamados/metrics` - Métricas do dashboard

### **Gestão de Chamados:**
- `POST /api/chamados/criar` - Criar novo chamado
- `POST /api/chamados/consultar` - Consultar chamado
- `POST /api/chamados/cadastrar-cidadao` - Cadastrar cidadão

### **Exemplos de Uso:**

#### **Criar Chamado:**
```json
POST /api/chamados/criar
{
    "cidadao_telefone": "+557798755764",
    "titulo": "Buraco na Rua",
    "descricao": "Tem um buraco grande na rua da minha casa",
    "endereco_ocorrencia": "Rua das Flores, 123, Centro",
    "fonte": "whatsapp"
}
```

#### **Consultar Chamado:**
```json
POST /api/chamados/consultar
{
    "protocolo": "INFRA-2024-001"
}
```

#### **Cadastrar Cidadão:**
```json
POST /api/chamados/cadastrar-cidadao
{
    "telefone": "+557798755764",
    "nome": "João Silva",
    "cpf": "12345678901",
    "email": "joao@email.com",
    "endereco": "Rua das Flores, 123, Centro"
}
```

---

## 🚀 COMO IMPLEMENTAR

### **1. Preparação do Ambiente:**
```bash
# No servidor
cd /root/projetos/cidadaoai-chatwoot
source venv/bin/activate
```

### **2. Instalar Dependências:**
```bash
pip install asyncpg==0.29.0
```

### **3. Aplicar Migration:**
```bash
# Executar script de migration
./apply_migration.sh
```

### **4. Verificar Banco:**
```bash
# Conectar no PostgreSQL
psql -h localhost -p 5433 -U cidadaoai_user -d cidadaoai

# Verificar tabelas criadas
\dt

# Verificar dados iniciais
SELECT * FROM prefeituras;
SELECT * FROM times;
SELECT * FROM categorias_chamados;
```

### **5. Deploy:**
```bash
# Fazer deploy das alterações
./update-server.sh
```

### **6. Testar Sistema:**
```bash
# Verificar status
curl https://tecnico.sisgov.app.br/api/chamados/status

# Verificar métricas
curl https://tecnico.sisgov.app.br/api/chamados/metrics
```

---

## 📊 DADOS INICIAIS INSERIDOS

### **Prefeitura Padrão:**
- Nome: "Prefeitura de Teste"
- Chatwoot Account ID: 1
- WhatsApp: "+557798755764"

### **Times/Secretarias:**
1. **Infraestrutura** - Buraco, iluminação, esgoto
2. **Saúde** - Posto, médico, remédio
3. **Educação** - Escola, merenda, transporte
4. **Assistência Social** - Bolsa, benefício, cadastro
5. **Obras** - Construção, reforma, pavimentação

### **Categorias de Chamados:**
- Buraco na Rua (24h SLA)
- Falta de Iluminação (48h SLA)
- Esgoto a Céu Aberto (12h SLA)
- Posto de Saúde (24h SLA)
- Merenda Escolar (168h SLA)
- Cadastro Único (120h SLA)
- Obra Pública (168h SLA)

### **Agentes IA:**
- Agente IA Geral
- Agente IA Cadastro
- Agente IA Infraestrutura

---

## 🔍 MONITORAMENTO E LOGS

### **Logs do Sistema:**
```bash
# Monitorar logs específicos do sistema de chamados
./monitor_ai_logs.sh | grep -i "chamado\|protocolo\|cidadão"
```

### **Verificar Status:**
```bash
# Status completo
curl https://tecnico.sisgov.app.br/api/chamados/status

# Métricas
curl https://tecnico.sisgov.app.br/api/chamados/metrics
```

### **Testar IA:**
```bash
# Testar endpoint de IA
curl -X POST https://tecnico.sisgov.app.br/api/agent/test \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tem um buraco na rua da minha casa",
    "conversation_id": 999,
    "contact_info": {
      "phone_number": "+557798755764",
      "name": "Teste"
    }
  }'
```

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

- [x] Schema do banco criado
- [x] Migration aplicada
- [x] Modelos Pydantic criados
- [x] Serviço de chamados implementado
- [x] IA especializada implementada
- [x] Endpoints criados
- [x] Integração com main.py
- [x] Dados iniciais inseridos
- [x] Scripts de migration criados
- [x] Documentação completa
- [x] Testes de integração

---

## 🎯 PRÓXIMOS PASSOS (FASE 2)

1. **Interface Web** - Dashboard para gestores
2. **Relatórios Avançados** - Analytics e métricas
3. **Notificações** - Alertas automáticos
4. **Integração Chatwoot** - Teams e atribuições
5. **Templates Dinâmicos** - Editor de respostas
6. **Multi-prefeitura** - Suporte completo

---

## 🆘 SOLUÇÃO DE PROBLEMAS

### **Erro de Conexão com Banco:**
```bash
# Verificar se PostgreSQL está rodando
systemctl status postgresql

# Verificar conexão
psql -h localhost -p 5433 -U cidadaoai_user -d cidadaoai
```

### **Erro na Migration:**
```bash
# Verificar logs
tail -f /var/log/postgresql/postgresql-*.log

# Executar migration manualmente
psql -h localhost -p 5433 -U cidadaoai_user -d cidadaoai -f backend/migrations/001_create_chamados_system.sql
```

### **IA Não Responde:**
```bash
# Verificar status da IA
curl https://tecnico.sisgov.app.br/api/agent/status

# Verificar logs da IA
./monitor_ai_logs.sh
```

---

## 📞 SUPORTE

Para dúvidas ou problemas:
1. Verificar logs do sistema
2. Consultar este manual
3. Testar endpoints individualmente
4. Verificar status dos serviços

**Sistema implementado com sucesso! 🎉**
