# Configuração do Chatwoot - Guia Completo

## 1. Configuração Inicial

### 1.1 Token de Acesso
- **Token fornecido**: `3kcYkVZPwDnRrCgVnLdFgtKY`
- **URL**: `https://app.chatwoot.com`

### 1.2 Configurar no Servidor
```bash
# Editar arquivo .env
nano .env

# Adicionar:
CHATWOOT_URL=https://app.chatwoot.com
CHATWOOT_API_TOKEN=3kcYkVZPwDnRrCgVnLdFgtKY
```

## 2. Configuração do WhatsApp

### 2.1 Criar Caixa de Entrada
1. Acesse: **Configurações > Canais > WhatsApp**
2. Clique em **"Adicionar Canal"**
3. Configure:
   - **Nome**: "WhatsApp SISGOV"
   - **Número**: Seu número do WhatsApp Business
   - **Webhook URL**: `http://SEU_SERVIDOR:8000/webhook/chatwoot`

### 2.2 Eventos do Webhook
Selecione os eventos:
- ✅ `message_created`
- ✅ `conversation_created`
- ✅ `conversation_updated`
- ✅ `conversation_status_changed`
- ✅ `contact_updated`

## 3. Configuração de Agentes

### 3.1 Criar Agente
1. Acesse: **Configurações > Agentes**
2. Clique em **"Adicionar Agente"**
3. Configure:
   - **Nome**: "Técnico SISGOV"
   - **Email**: `tecnico@sisgov.app.br`
   - **Senha**: Definir senha segura
   - **Permissões**: Administrador

### 3.2 Atribuir à Caixa de Entrada
1. Acesse: **Configurações > Canais > WhatsApp**
2. Selecione sua caixa de entrada
3. Em **"Agentes"**, adicione o agente criado

## 4. Teste da Integração

### 4.1 Testar API
```bash
# Executar script de teste
python test_chatwoot_api.py
```

### 4.2 Testar Webhook
1. Envie uma mensagem para o WhatsApp
2. Verifique se aparece no painel técnico
3. Responda pelo painel técnico
4. Verifique se chega no WhatsApp

## 5. Fluxo Completo

1. **Usuário** envia mensagem no WhatsApp
2. **Chatwoot** recebe e envia webhook
3. **Backend** processa webhook
4. **Frontend** mostra nova conversa
5. **Técnico** responde pelo painel
6. **Chatwoot** envia resposta para WhatsApp

## 6. Troubleshooting

### 6.1 Webhook não funciona
- Verificar se URL está acessível
- Verificar se eventos estão selecionados
- Verificar logs do backend

### 6.2 API não funciona
- Verificar token de acesso
- Verificar permissões do agente
- Verificar URL da API

### 6.3 Mensagens não aparecem
- Verificar auto-refresh do frontend
- Verificar conexão com API
- Verificar logs do console
