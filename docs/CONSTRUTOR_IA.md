# 🤖 Cidadão.AI - Construtor de Agentes IA

## 🎯 **O que é o Construtor de IA?**

O Construtor de IA é uma interface visual que permite criar, configurar e testar agentes de inteligência artificial **sem precisar programar**. É como um "WordPress para IA" - você constrói agentes através de uma interface amigável.

## 🚀 **Vantagens Principais**

### ✅ **1. Desenvolvimento 10x Mais Rápido**
- **Antes:** Código + Deploy + Teste = 2-4 horas
- **Agora:** Interface + Teste = 5-10 minutos

### ✅ **2. Acesso para Não-Programadores**
- Gestores podem criar agentes
- Técnicos podem ajustar respostas
- Sem dependência de desenvolvedor

### ✅ **3. Teste em Tempo Real**
- Simulador de conversa
- Métricas de performance
- Ajuste instantâneo de parâmetros

### ✅ **4. Templates Pré-definidos**
- Agentes prontos para cada categoria
- Fluxos otimizados
- Boas práticas incorporadas

### ✅ **5. Versionamento e Backup**
- Histórico de mudanças
- Rollback de configurações
- A/B testing de prompts

## 🏗️ **Como Funciona**

### 📋 **Estrutura do Agente**

```json
{
  "name": "Agente de Infraestrutura",
  "provider": "groq",
  "category": "infraestrutura",
  "sla": 24,
  "priority": "alta",
  "system_prompt": "Você é um assistente especializado...",
  "flow": [
    {"step": "initial", "action": "detect_new_conversation"},
    {"step": "greeting", "action": "greet_citizen"},
    {"step": "data_collection", "action": "collect_citizen_data"}
  ],
  "templates": {
    "greeting": "Olá! Como posso te ajudar?",
    "confirmation": "Confirme se os dados estão corretos..."
  }
}
```

### 🔄 **Fluxo de Criação**

1. **Escolha o Template** - Selecione categoria (Infraestrutura, Saúde, etc.)
2. **Configure o Agente** - Nome, provedor, SLA, prioridade
3. **Edite o Prompt** - Personalize o comportamento da IA
4. **Defina o Fluxo** - Configure etapas da conversa
5. **Teste** - Simule conversas e ajuste parâmetros
6. **Deploy** - Ative o agente no sistema

## 🎨 **Interface do Construtor**

### 🖥️ **Acesso:**
- **URL:** https://tecnico.sisgov.app.br/ai-builder
- **Requer:** Acesso administrativo

### 📱 **Funcionalidades:**

#### **1. Configurações do Agente**
- Nome e descrição
- Provedor de IA (Groq, OpenAI, Anthropic)
- Categoria e SLA
- Prioridade e configurações

#### **2. Editor de Prompt**
- Editor visual com syntax highlighting
- Templates pré-definidos
- Parâmetros ajustáveis (temperatura, tokens)

#### **3. Designer de Fluxo**
- Visualização das etapas
- Drag & drop para reordenação
- Configuração de ações

#### **4. Simulador de Teste**
- Chat em tempo real
- Métricas de performance
- Análise de custos

## 🔧 **APIs Disponíveis**

### 📡 **Endpoints do Construtor**

```bash
# Obter templates disponíveis
GET /api/ai-builder/templates

# Listar agentes criados
GET /api/ai-builder/agents

# Criar novo agente
POST /api/ai-builder/agents
Body: {
  "name": "Meu Agente",
  "provider": "groq",
  "category": "infraestrutura",
  "system_prompt": "...",
  "flow": [...],
  "templates": {...}
}

# Atualizar agente
PUT /api/ai-builder/agents/{agent_id}

# Testar configuração
POST /api/ai-builder/test
Body: {
  "config": {...},
  "message": "Mensagem de teste"
}
```

## 🎯 **Casos de Uso**

### 🏛️ **Para Prefeituras:**

#### **1. Agente de Infraestrutura**
- Atende buracos, iluminação, vazamentos
- SLA: 24 horas
- Prioridade: Alta

#### **2. Agente de Saúde**
- Agendamentos, emergências, vacinação
- SLA: 4 horas
- Prioridade: Crítica

#### **3. Agente de Educação**
- Matrículas, transporte escolar, merenda
- SLA: 48 horas
- Prioridade: Média

#### **4. Agente de Assistência Social**
- Benefícios, cadastros, orientações
- SLA: 72 horas
- Prioridade: Média

### 🏢 **Para Empresas:**

#### **1. Agente de Vendas**
- Qualificação de leads
- Agendamento de reuniões
- Follow-up de clientes

#### **2. Agente de Suporte**
- Resolução de problemas
- Escalação de tickets
- Base de conhecimento

#### **3. Agente de RH**
- Recrutamento inicial
- Agendamento de entrevistas
- Orientações para candidatos

## 📊 **Métricas e Monitoramento**

### 📈 **Dashboard de Performance**
- Tempo de resposta
- Taxa de sucesso
- Custo por conversa
- Satisfação do usuário

### 🔍 **Análise de Conversas**
- Sentimentos das mensagens
- Padrões de problemas
- Otimização de fluxos
- Identificação de gargalos

## 🚀 **Implementação**

### 📋 **Pré-requisitos**
- Sistema Cidadão.AI funcionando
- Acesso administrativo
- Chaves de API configuradas

### ⚡ **Deploy Rápido**

```bash
# 1. Acesse o construtor
https://tecnico.sisgov.app.br/ai-builder

# 2. Escolha um template
Selecione categoria (Infraestrutura, Saúde, etc.)

# 3. Configure o agente
Ajuste nome, SLA, prioridade

# 4. Personalize o prompt
Edite o comportamento da IA

# 5. Teste o agente
Use o simulador de conversa

# 6. Salve e ative
Deploy automático no sistema
```

### 🔧 **Configuração Avançada**

```bash
# Acesse via API
curl -X POST https://tecnico.sisgov.app.br/api/ai-builder/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Agente Personalizado",
    "provider": "groq",
    "category": "infraestrutura",
    "system_prompt": "Seu prompt customizado aqui...",
    "sla": 12,
    "priority": "critica"
  }'
```

## 📚 **Exemplos Práticos**

### 🏗️ **Agente de Infraestrutura**

**Prompt:**
```
Você é um assistente especializado em infraestrutura urbana.
Coleta dados do cidadão e categoriza problemas como:
- Buracos nas ruas
- Iluminação pública
- Vazamentos de água
- Danos em calçadas

Sempre confirme informações e gere protocolo único.
```

**Fluxo:**
1. Boas-vindas
2. Coleta de dados (nome, telefone, endereço)
3. Descrição do problema
4. Categorização automática
5. Confirmação dos dados
6. Geração de protocolo

### 🏥 **Agente de Saúde**

**Prompt:**
```
Você é um assistente de saúde pública.
Priorize casos urgentes e oriente sobre:
- Agendamentos
- Emergências médicas
- Vacinação
- Programas de saúde

Para emergências, oriente a ligar 192.
```

**Fluxo:**
1. Boas-vindas
2. Verificação de urgência
3. Coleta de dados
4. Categorização do problema
5. Orientação específica
6. Geração de protocolo

## 🔮 **Próximas Funcionalidades**

### 📅 **Versão 2.0**
- [ ] Editor visual de fluxos (drag & drop)
- [ ] Biblioteca de componentes reutilizáveis
- [ ] Integração com ferramentas externas
- [ ] Analytics avançados

### 📅 **Versão 3.0**
- [ ] IA para criar IA (auto-generation)
- [ ] Machine learning para otimização
- [ ] Integração com CRM/ERP
- [ ] Multi-idiomas

## 💡 **Dicas de Uso**

### ✅ **Boas Práticas**

1. **Comece com templates** - Use exemplos como base
2. **Teste sempre** - Use o simulador antes de ativar
3. **Seja específico** - Prompts claros geram melhores respostas
4. **Monitore métricas** - Ajuste baseado em performance
5. **Versionamento** - Mantenha backup das configurações

### ❌ **Evite**

1. Prompts muito genéricos
2. Fluxos muito complexos
3. SLA irrealistas
4. Falta de testes
5. Ausência de monitoramento

## 🆘 **Suporte**

### 📞 **Em caso de problemas:**
1. Consulte os logs do sistema
2. Teste com mensagens simples
3. Verifique configurações da API
4. Use o modo de debug

### 🔗 **Links Úteis:**
- **Construtor:** https://tecnico.sisgov.app.br/ai-builder
- **Admin:** https://tecnico.sisgov.app.br/admin
- **API Docs:** https://tecnico.sisgov.app.br/docs
- **Troubleshooting:** docs/TROUBLESHOOTING.md

---

**📅 Última atualização:** 29 de Dezembro de 2024  
**🤖 Versão:** 1.0.0  
**👨‍💻 Desenvolvido por:** Equipe Cidadão.AI
