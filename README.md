# 🏛️ Cidadão.AI - Sistema de Chamados para Prefeituras

Sistema completo de atendimento ao cidadão via WhatsApp, integrado com Chatwoot, que permite cadastro automático, categorização inteligente de chamados e gestão administrativa.

## 🚀 Status do Projeto

**✅ FASE 1 - IMPLEMENTADA E FUNCIONANDO**

- 🤖 IA especializada para atendimento
- 📋 Cadastro automático de cidadãos
- 🏷️ Categorização inteligente de chamados
- 📊 Geração automática de protocolos
- 🖥️ Dashboard administrativo
- 📱 Interface web completa

## 🎯 Funcionalidades Principais

### 🤖 Sistema de IA
- **Cadastro Automático:** Coleta dados do cidadão via conversa natural
- **Categorização Inteligente:** Classifica chamados por secretaria automaticamente
- **Memória de Conversas:** Lembra interações anteriores
- **Confirmação:** Sempre confirma categoria antes de finalizar

### 📊 Gestão Administrativa
- **Dashboard em Tempo Real:** Métricas e estatísticas
- **Gestão de Cidadãos:** Lista completa com filtros
- **Gestão de Chamados:** Acompanhamento de protocolos
- **Status do Sistema:** Monitoramento de saúde

### 🔧 Sistema Técnico
- **APIs RESTful:** Endpoints completos para integração
- **Banco PostgreSQL:** Schema estruturado e otimizado
- **Deploy Automatizado:** Docker Swarm + Nginx
- **Monitoramento:** Logs estruturados e métricas

## 🌐 Acesso ao Sistema

- **Dashboard Técnico:** https://tecnico.sisgov.app.br/
- **Painel Administrativo:** https://tecnico.sisgov.app.br/admin
- **Documentação da API:** https://tecnico.sisgov.app.br/docs
- **Status do Sistema:** https://tecnico.sisgov.app.br/api/chamados/status

## 📚 Documentação

### 📖 Manuais Principais
- **[📚 Manual Completo do Sistema](docs/MANUAL_COMPLETO_SISTEMA.md)** - Documentação completa
- **[🔧 Guia de Troubleshooting](docs/TROUBLESHOOTING.md)** - Solução de problemas
- **[⚡ Comandos Rápidos](COMANDOS_RAPIDOS.md)** - Referência de comandos
- **[📋 Manual de Implementação](docs/MANUAL_IMPLEMENTACAO_FASE1.md)** - Setup e deploy

### 🔗 Links Úteis
- **[🏗️ Schema do Banco](docs/database_schema.sql)** - Estrutura completa
- **[🔄 Fluxo do Sistema](docs/fluxo_sistema.md)** - Processo de atendimento
- **[📊 Migration SQL](backend/migrations/001_create_chamados_system.sql)** - Script de criação

## 🚀 Instalação e Deploy

### 📋 Pré-requisitos
- Docker e Docker Swarm
- PostgreSQL 13+
- Python 3.12+
- Acesso SSH ao servidor

### ⚡ Deploy Rápido

```bash
# 1. Clone o repositório
git clone https://github.com/valleteclab/cidadaoai-chatwoot.git
cd cidadaoai-chatwoot

# 2. Configure as variáveis de ambiente
cp env.template .env
nano .env  # Configure suas chaves de API

# 3. Execute o deploy
./update-server.sh
```

### 🔧 Configuração Manual

```bash
# Acesse o servidor
ssh root@212.85.0.166

# Navegue para o projeto
cd /root/projetos/cidadaoai-chatwoot

# Ative o ambiente virtual
source venv/bin/activate

# Aplique a migration do banco
./apply_migration.sh

# Faça o deploy
./update-server.sh
```

## 🏗️ Arquitetura

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

### 🛠️ Stack Tecnológica
- **Backend:** FastAPI + Python 3.12
- **Banco:** PostgreSQL + asyncpg
- **IA:** Groq API (Llama 3.1)
- **Frontend:** HTML + Tailwind CSS + Alpine.js
- **Deploy:** Docker Swarm + Nginx + Traefik

## 📱 Como Usar

### 👥 Para Cidadãos
1. Envie uma mensagem para o WhatsApp da prefeitura
2. A IA irá te guiar no cadastro (se necessário)
3. Descreva seu problema ou solicitação
4. Receba um protocolo único
5. Acompanhe o status via WhatsApp

### 👨‍💼 Para Administradores
1. Acesse https://tecnico.sisgov.app.br/admin
2. Visualize métricas em tempo real
3. Gerencie cidadãos e chamados
4. Monitore o status do sistema

## 🔍 Monitoramento

### 📊 Comandos Úteis

```bash
# Status do serviço
docker service ps cidadaoai_app

# Logs em tempo real
docker service logs -f cidadaoai_app

# Status da API
curl https://tecnico.sisgov.app.br/api/chamados/status

# Métricas do sistema
curl https://tecnico.sisgov.app.br/api/chamados/metrics
```

### 🗄️ Banco de Dados

```bash
# Conectar ao PostgreSQL
PGPASSWORD="cidadaoai_senha_2024" psql -h 212.85.0.166 -p 5433 -U cidadaoai_user -d cidadaoai

# Ver cidadãos cadastrados
SELECT id, nome, telefone, email, created_at FROM cidadaos ORDER BY created_at DESC LIMIT 10;

# Ver chamados
SELECT id, protocolo, titulo, status, created_at FROM chamados ORDER BY created_at DESC LIMIT 10;
```

## 🚀 Próximas Fases

### 📅 Fase 2 - Interface de Gestão (Q1 2025)
- [ ] Dashboard avançado com gráficos
- [ ] Editor de templates para IA
- [ ] Sistema de notificações
- [ ] Relatórios personalizados

### 📅 Fase 3 - Multi-Prefeitura (Q2 2025)
- [ ] Suporte multi-tenant
- [ ] Configurações por prefeitura
- [ ] API pública
- [ ] App mobile para gestores

### 📅 Fase 4 - Automações Avançadas (Q3 2025)
- [ ] Workflows automatizados
- [ ] Integração com sistemas externos
- [ ] Chatbot especializado por secretaria
- [ ] Análise de sentimento

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 📞 Suporte

### 🆘 Em caso de problemas:
1. Consulte o [Guia de Troubleshooting](docs/TROUBLESHOOTING.md)
2. Verifique os [Comandos Rápidos](COMANDOS_RAPIDOS.md)
3. Execute o diagnóstico do sistema

### 🔗 Links de Acesso:
- **Servidor:** ssh root@212.85.0.166
- **Dashboard:** https://tecnico.sisgov.app.br/
- **Admin:** https://tecnico.sisgov.app.br/admin
- **API:** https://tecnico.sisgov.app.br/docs

---

**📅 Última atualização:** 29 de Dezembro de 2024  
**👨‍💻 Desenvolvido por:** Equipe Cidadão.AI  
**🏛️ Versão:** 1.0.0 (Fase 1)  
**🌟 Status:** ✅ Implementado e Funcionando
