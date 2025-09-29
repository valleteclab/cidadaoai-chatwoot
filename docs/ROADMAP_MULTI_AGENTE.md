# 🤖 Cidadão.AI - Roadmap Sistema Multi-Agente

## 📋 **Tarefas Prioritárias para Próxima Sessão**

### 🎯 **FASE 2 - Sistema Multi-Agente Especializado**

---

## 🚀 **1. Arquitetura Multi-Agente (PRIORIDADE ALTA)**

### 📋 **Tarefas:**
- [ ] **Definir padrão JSON** para comunicação entre agentes
- [ ] **Implementar Agente de Categorização** especializado
- [ ] **Implementar Agente de Chamados** dedicado
- [ ] **Criar sistema de roteamento** entre agentes
- [ ] **Implementar fila de mensagens** para comunicação

### 🔄 **Fluxo Proposto:**
```
Cidadão → Agente Categorização → Agente Chamados → Sistema Protocolos
   ↓              ↓                    ↓                ↓
WhatsApp    Detecta problema    Abre chamado      Gera protocolo
            Categoriza tipo     Coleta dados      Retorna número
```

### 📊 **Estrutura JSON:**
```json
{
  "event": "create_ticket",
  "from_agent": "categorization_agent",
  "to_agent": "ticket_agent",
  "conversation_id": 12345,
  "data": {
    "citizen_id": 123,
    "category": "infraestrutura",
    "problem_type": "buraco_rua",
    "description": "Buraco na Rua X, número Y",
    "address": "Rua das Flores, 123",
    "priority": "alta",
    "sla_hours": 24,
    "contact_info": {
      "phone": "+557798755764",
      "name": "João Silva"
    }
  },
  "timestamp": "2025-01-01T12:00:00Z"
}
```

---

## ⚡ **2. Avaliação Agno Framework (PRIORIDADE MÉDIA)**

### 📋 **Tarefas:**
- [ ] **Instalar e configurar Agno** no ambiente de desenvolvimento
- [ ] **Criar protótipo** com Agno AgentOS
- [ ] **Implementar agente de teste** usando Agno
- [ ] **Comparar performance** com implementação atual
- [ ] **Avaliar facilidade** de desenvolvimento
- [ ] **Testar multi-agente** com Agno

### 🎯 **Critérios de Avaliação:**
- **Performance:** Tempo de resposta, throughput
- **Facilidade:** Setup, desenvolvimento, manutenção
- **Recursos:** Multi-agente, memory, session management
- **Custo:** Infraestrutura, licenciamento
- **Compatibilidade:** Integração com sistema atual

### 📊 **Comparação Agno vs Atual:**
| Aspecto | Implementação Atual | Agno Framework |
|---------|-------------------|----------------|
| **Setup** | ⭐⭐⭐ Médio | ⭐⭐⭐⭐⭐ Rápido |
| **Performance** | ⭐⭐⭐⭐ Boa | ⭐⭐⭐⭐⭐ Excelente |
| **Multi-agente** | ⭐⭐ Manual | ⭐⭐⭐⭐⭐ Nativo |
| **Interface** | ⭐⭐⭐⭐ Custom | ⭐⭐⭐⭐⭐ AgentOS |
| **Privacidade** | ⭐⭐⭐⭐⭐ Total | ⭐⭐⭐⭐⭐ Total |
| **Custo** | ⭐⭐⭐⭐⭐ Baixo | ⭐⭐⭐⭐ Médio |

---

## 🔧 **3. Implementação Técnica**

### 📋 **Estrutura de Arquivos:**
```
backend/
├── agents/
│   ├── base_agent.py           # Classe base para agentes
│   ├── categorization_agent.py # Agente de categorização
│   ├── ticket_agent.py         # Agente de chamados
│   ├── protocol_agent.py       # Agente de protocolos
│   └── agent_router.py         # Roteador entre agentes
├── communication/
│   ├── message_queue.py        # Fila de mensagens
│   ├── agent_bus.py           # Barramento de comunicação
│   └── event_handler.py       # Manipulador de eventos
└── ai_builder_service.py      # Serviço atual (manter)
```

### 🔄 **Padrão de Comunicação:**
```python
class AgentMessage:
    event: str
    from_agent: str
    to_agent: str
    conversation_id: int
    data: Dict[str, Any]
    timestamp: datetime
    priority: int = 0
    retry_count: int = 0
```

---

## 📊 **4. Métricas e Monitoramento**

### 📋 **Tarefas:**
- [ ] **Dashboard de agentes** em tempo real
- [ ] **Métricas de performance** por agente
- [ ] **Logs estruturados** para debugging
- [ ] **Alertas automáticos** para falhas
- [ ] **Analytics de conversas** entre agentes

### 📈 **KPIs a Monitorar:**
- Tempo de resposta por agente
- Taxa de sucesso na categorização
- Número de chamados criados
- Tempo médio de resolução
- Satisfação do cidadão

---

## 🎯 **5. Casos de Uso Específicos**

### 🏗️ **Agente de Infraestrutura:**
- Detecta: buracos, iluminação, vazamentos
- Categoriza: tipo, urgência, localização
- Aciona: Agente de Chamados
- SLA: 24 horas

### 🏥 **Agente de Saúde:**
- Detecta: agendamentos, emergências, vacinação
- Categoriza: urgência, tipo de serviço
- Aciona: Agente de Chamados + Notificação
- SLA: 4 horas

### 🎓 **Agente de Educação:**
- Detecta: matrículas, transporte, merenda
- Categoriza: período, modalidade
- Aciona: Agente de Chamados
- SLA: 48 horas

---

## 🚀 **6. Cronograma de Implementação**

### 📅 **Semana 1:**
- [ ] Implementar padrão JSON
- [ ] Criar Agente de Categorização
- [ ] Testar comunicação básica

### 📅 **Semana 2:**
- [ ] Implementar Agente de Chamados
- [ ] Criar sistema de roteamento
- [ ] Testar fluxo completo

### 📅 **Semana 3:**
- [ ] Avaliar Agno Framework
- [ ] Comparar performance
- [ ] Decidir sobre migração

### 📅 **Semana 4:**
- [ ] Implementar monitoramento
- [ ] Criar dashboard de agentes
- [ ] Documentar sistema

---

## 🔍 **7. Critérios de Sucesso**

### ✅ **Funcional:**
- [ ] Agentes se comunicam via JSON
- [ ] Categorização automática funciona
- [ ] Chamados são criados automaticamente
- [ ] Protocolos são gerados corretamente

### ✅ **Performance:**
- [ ] Tempo de resposta < 2 segundos
- [ ] Taxa de sucesso > 95%
- [ ] Zero perda de mensagens
- [ ] Escalabilidade para 100+ conversas simultâneas

### ✅ **Usabilidade:**
- [ ] Interface de monitoramento intuitiva
- [ ] Logs claros para debugging
- [ ] Alertas automáticos funcionais
- [ ] Documentação completa

---

## 📚 **8. Recursos e Referências**

### 🔗 **Links Úteis:**
- [Agno Documentation](https://docs.agno.com/introduction)
- [AgentOS Framework](https://docs.agno.com/agentos)
- [Multi-Agent Systems](https://docs.agno.com/concepts/agents)

### 📖 **Documentação:**
- [Manual do Construtor](docs/CONSTRUTOR_IA.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Comandos Rápidos](COMANDOS_RAPIDOS.md)

---

## 🎯 **Resumo das Prioridades**

### 🔥 **URGENTE:**
1. **Implementar padrão JSON** para comunicação
2. **Criar Agente de Categorização** especializado
3. **Implementar Agente de Chamados** dedicado

### ⚡ **IMPORTANTE:**
4. **Avaliar Agno Framework** para possível migração
5. **Criar sistema de monitoramento** de agentes
6. **Implementar dashboard** em tempo real

### 📋 **DESEJÁVEL:**
7. **Documentar arquitetura** completa
8. **Criar testes automatizados** para agentes
9. **Implementar analytics** avançados

---

**📅 Última atualização:** 29 de Dezembro de 2024  
**🎯 Status:** Pronto para implementação  
**👨‍💻 Próxima sessão:** Foco em arquitetura multi-agente
