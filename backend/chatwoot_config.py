"""
Configurações e constantes para integração com Chatwoot
"""

# Eventos de webhook suportados pelo Chatwoot
SUPPORTED_WEBHOOK_EVENTS = [
    "message_created",
    "message_updated", 
    "conversation_created",
    "conversation_updated",
    "conversation_status_changed",
    "contact_updated",
    "conversation_typing_on",
    "conversation_typing_off"
]

# Tipos de mensagem
MESSAGE_TYPES = {
    "incoming": 0,
    "outgoing": 1
}

# Tipos de remetente
SENDER_TYPES = {
    "contact": "Contact",
    "user": "User"
}

# Status de conversa
CONVERSATION_STATUS = {
    "open": "open",
    "resolved": "resolved", 
    "pending": "pending"
}

# Canais suportados
CHANNELS = {
    "whatsapp": "Channel::Whatsapp",
    "web": "Channel::WebWidget",
    "facebook": "Channel::FacebookPage",
    "twitter": "Channel::TwitterProfile"
}

# Configurações de API
CHATWOOT_API_BASE_URL = "https://app.chatwoot.com/api/v1"
CHATWOOT_WEBHOOK_BASE_URL = "https://app.chatwoot.com/api/v1"

# Headers padrão para requisições
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}
