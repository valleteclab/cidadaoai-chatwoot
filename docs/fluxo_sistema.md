# FLUXO COMPLETO DO SISTEMA DE CHAMADOS CIDADÃOS

## 🎯 VISÃO GERAL
Sistema integrado com Chatwoot para gestão de chamados cidadãos via WhatsApp, com IA para cadastro, categorização e atendimento.

## 📱 FLUXO PRINCIPAL

### 1. PRIMEIRA INTERAÇÃO
```
Cidadão envia: "Tem um buraco na rua da minha casa"
     ↓
IA detecta: Primeira mensagem
     ↓
IA responde: "Olá! Para abrir um chamado, preciso cadastrá-lo primeiro..."
     ↓
IA coleta: Nome, CPF, Endereço, Email (opcional)
     ↓
Sistema: Salva cidadão no banco
     ↓
IA continua: "Perfeito! Agora sobre o buraco na rua..."
```

### 2. CATEGORIZAÇÃO AUTOMÁTICA
```
IA analisa: "buraco na rua" + palavras-chave
     ↓
IA identifica: Categoria = "Buraco na Rua" → Time = "Infraestrutura"
     ↓
IA confirma: "Seu chamado é sobre Infraestrutura (buraco na rua), está correto?"
     ↓
Cidadão: "Sim" ou "Não, é sobre..."
     ↓
Se não: IA repete processo
Se sim: Continua
```

### 3. CRIAÇÃO DO CHAMADO
```
Sistema: Gera protocolo "INFRA-2024-001"
     ↓
IA coleta: Endereço específico do buraco
     ↓
Sistema: Salva chamado no banco
     ↓
IA atribui: Chamado para Time "Infraestrutura" no Chatwoot
     ↓
IA responde: "✅ Chamado criado! Protocolo: INFRA-2024-001"
```

### 4. ACOMPANHAMENTO
```
Cidadão pergunta: "Status do protocolo INFRA-2024-001"
     ↓
IA consulta: Banco de dados
     ↓
IA responde: "Seu chamado está em andamento. Previsão: 24h"
```

## 🏗️ ARQUITETURA TÉCNICA

### COMPONENTES PRINCIPAIS
1. **Chatwoot** - Interface de conversas
2. **Sistema Cidadão.AI** - Lógica de negócio
3. **Banco PostgreSQL** - Dados persistentes
4. **IA (Groq)** - Processamento inteligente
5. **Frontend** - Interface administrativa

### INTEGRAÇÕES
- **WhatsApp** ↔ **Chatwoot** ↔ **Sistema Cidadão.AI**
- **IA** ↔ **Banco de Dados** ↔ **Chatwoot Teams**

## 📊 FUNCIONALIDADES

### PARA CIDADÃOS (via WhatsApp)
- ✅ Cadastro automático
- ✅ Abertura de chamados
- ✅ Consulta de status
- ✅ Acompanhamento de protocolos
- ✅ Recebimento de atualizações

### PARA AGENTES HUMANOS (Chatwoot)
- ✅ Visualizar conversas
- ✅ Responder cidadãos
- ✅ Atribuir chamados
- ✅ Alterar status
- ✅ Adicionar comentários

### PARA GESTORES (Frontend)
- ✅ Relatórios por time
- ✅ Métricas de SLA
- ✅ Análise de categorias
- ✅ Gestão de agentes
- ✅ Configuração de IA

## 🔄 ESTADOS DO CHAMADO

1. **ABERTO** - Recém criado
2. **EM_ANDAMENTO** - Sendo atendido
3. **RESOLVIDO** - Concluído
4. **CANCELADO** - Cancelado pelo cidadão

## 📈 RELATÓRIOS DISPONÍVEIS

- Chamados por time/secretaria
- Tempo médio de resolução
- Categorias mais frequentes
- Performance por agente
- SLA compliance
- Satisfação do cidadão

## 🎛️ CONFIGURAÇÕES FLEXÍVEIS

- **Palavras-chave** por categoria
- **SLA** por tipo de chamado
- **Templates** de resposta
- **Prompts** de IA personalizáveis
- **Workflows** de aprovação
- **Notificações** automáticas
