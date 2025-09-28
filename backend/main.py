# backend/main.py
"""
Cidadão.AI - Backend com Chatwoot
"""
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import UploadFile, File, Form
from backend.websocket_manager import ws_manager, app as socketio_app
from backend.attachment_service import AttachmentService
from backend.models import ChatwootAttachment, ImageUploadRequest, ImageUploadResponse
from fastapi.responses import FileResponse
import httpx
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import redis.asyncio as redis
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from openai import OpenAI
import logging
from backend.media_handler import media_handler
from backend.audio_transcriber import transcriber
from backend.ai_agent import ai_agent

# Configurar logging primeiro
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
logger.info("🔧 Verificando configurações...")
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
logger.info(f"📂 Procurando .env em: {env_path}")

if os.path.exists(env_path):
    logger.info("✅ Arquivo .env encontrado")
    load_dotenv(env_path)
    
    # Debug: mostrar conteúdo do .env (sem mostrar valores completos)
    with open(env_path) as f:
        env_contents = f.readlines()
        logger.info("📋 Variáveis no .env:")
        for line in env_contents:
            if line.strip() and not line.startswith('#'):
                key = line.split('=')[0]
                logger.info(f"   - {key}: {'✅ Configurada' if os.getenv(key) else '❌ Não configurada'}")
else:
    logger.error("❌ Arquivo .env não encontrado!")
logger.info(f"Arquivo .env: {'✅ Encontrado' if os.path.exists('.env') else '❌ Não encontrado'}")

# OpenAI será inicializado sob demanda quando necessário
logger.info("OpenAI será inicializado quando necessário")

# Inicializar serviços
attachment_service = AttachmentService()

app = FastAPI(
    title="Cidadão.AI - Backend API", 
    description="API para processamento de mensagens do WhatsApp e gestão de chamados.",
    version="1.0.0"
)

# Montar aplicativo Socket.IO (usar caminho padrão /socket.io)
app.mount("/socket.io", socketio_app)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://tecnico.sisgov.app.br",
        "http://tecnico.sisgov.app.br",
        "https://chat.sisgov.app.br"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Servir arquivos estáticos do frontend
app.mount("/static", StaticFiles(directory="frontend/tecnico"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")

# Rotas explícitas para a página HTML
@app.get("/", include_in_schema=False)
async def index():
    return FileResponse("frontend/tecnico/index.html")

@app.get("/tecnico", include_in_schema=False)
async def tecnico():
    return FileResponse("frontend/tecnico/index.html")

# Configurações
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHATWOOT_URL = os.getenv("CHATWOOT_URL")
CHATWOOT_API_TOKEN = os.getenv("CHATWOOT_API_TOKEN")
CHATWOOT_ACCOUNT_ID = int(os.getenv("CHATWOOT_ACCOUNT_ID", "1"))  # ID da conta no Chatwoot
# CHATWOOT_WEBHOOK_SECRET não é mais necessário - Chatwoot não oferece verificação HMAC
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://cidadaoai_user:cidadaoai_senha_2024@localhost:5433/cidadaoai")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6380")

# Inicializar clientes
openai_client = None
if OPENAI_API_KEY:
    try:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("OpenAI client initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize OpenAI client: {str(e)}")
        openai_client = None
else:
    logger.warning("OPENAI_API_KEY not configured - AI features disabled")

redis_client = redis.from_url(REDIS_URL)

# Utilidades para Chatwoot
def extract_chatwoot_payload(api_response: Any) -> List[Dict[str, Any]]:
    """Extrai a lista de itens retornada pela API do Chatwoot independentemente do formato.

    Algumas versões retornam em payload no topo (data["payload"]) e outras retornam em data.payload.
    Esta função tenta ambos os formatos e retorna sempre uma lista.
    """
    try:
        if not isinstance(api_response, dict):
            return []

        # Formato 1: { "payload": [...] }
        if "payload" in api_response and isinstance(api_response["payload"], list):
            return api_response["payload"]

        # Formato 2: { "data": { "payload": [...] } }
        data_obj = api_response.get("data")
        if isinstance(data_obj, dict) and isinstance(data_obj.get("payload"), list):
            return data_obj["payload"]

        # Formato 3: { "data": [...] }
        if isinstance(data_obj, list):
            return data_obj
    except Exception:
        pass
    return []

# Modelos Pydantic
class WebhookPayload(BaseModel):
    """Modelo para webhook do Chatwoot"""
    event: str
    data: Dict[str, Any]

class MessageData(BaseModel):
    """Modelo para dados de mensagem"""
    id: int
    content: str
    message_type: str
    sender: Dict[str, Any]
    conversation: Dict[str, Any]
    account: Dict[str, Any]
    inbox: Dict[str, Any]

# Endpoints básicos
@app.get("/health", tags=["Status"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/agent/status", tags=["AI Agent"])
async def get_agent_status():
    """Verificar status do agente IA"""
    try:
        return {
            "status": "success",
            "agent_available": ai_agent.is_available(),
            "current_provider": ai_agent.get_provider_name(),
            "groq_configured": bool(os.getenv("GROQ_API_KEY")),
            "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
            "anthropic_configured": bool(os.getenv("ANTHROPIC_API_KEY")),
            "conversation_memory_count": len(ai_agent.conversation_memory),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error checking agent status: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/agent/debug", tags=["AI Agent"])
async def get_agent_debug():
    """Debug info do agente IA"""
    try:
        return {
            "status": "success",
            "agent_available": ai_agent.is_available(),
            "current_provider": ai_agent.get_provider_name(),
            "groq_configured": bool(os.getenv("GROQ_API_KEY")),
            "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
            "anthropic_configured": bool(os.getenv("ANTHROPIC_API_KEY")),
            "conversation_memory": {
                "total_conversations": len(ai_agent.conversation_memory),
                "conversation_ids": list(ai_agent.conversation_memory.keys())
            },
            "environment": {
                "groq_key_set": bool(os.getenv("GROQ_API_KEY")),
                "groq_key_length": len(os.getenv("GROQ_API_KEY", "")) if os.getenv("GROQ_API_KEY") else 0,
                "openai_key_set": bool(os.getenv("OPENAI_API_KEY")),
                "openai_key_length": len(os.getenv("OPENAI_API_KEY", "")) if os.getenv("OPENAI_API_KEY") else 0,
                "anthropic_key_set": bool(os.getenv("ANTHROPIC_API_KEY")),
                "anthropic_key_length": len(os.getenv("ANTHROPIC_API_KEY", "")) if os.getenv("ANTHROPIC_API_KEY") else 0
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting agent debug info: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Variável global para armazenar logs de IA
ai_logs = []

@app.get("/api/agent/logs", tags=["AI Agent"])
async def get_ai_logs():
    """Obter logs de IA em tempo real"""
    return {
        "status": "success",
        "logs": ai_logs[-50:],  # Últimos 50 logs
        "total_logs": len(ai_logs),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/agent/log", tags=["AI Agent"])
async def add_ai_log(log_data: dict):
    """Adicionar log de IA (para uso interno)"""
    global ai_logs
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "type": log_data.get("type", "info"),
        "message": log_data.get("message", ""),
        "data": log_data.get("data", {})
    }
    ai_logs.append(log_entry)
    
    # Manter apenas os últimos 1000 logs
    if len(ai_logs) > 1000:
        ai_logs = ai_logs[-1000:]
    
    return {"status": "success"}

# Webhook endpoint para Chatwoot
@app.post("/webhook/chatwoot", tags=["Webhooks"])
async def chatwoot_webhook(request: Request):
    """
    Endpoint para receber webhooks do Chatwoot
    
    Processa eventos como:
    - message_created: Nova mensagem recebida
    - conversation_created: Nova conversa criada
    - conversation_updated: Conversa atualizada
    - contact_updated: Contato atualizado
    """
    try:
        # Receber payload bruto
        payload = await request.json()
        logger.info(f"Received webhook payload: {json.dumps(payload, indent=2)}")
        
        # Extrair evento
        event = payload.get("event")
        if not event:
            logger.warning("No event found in payload")
            return {"status": "error", "message": "No event found"}
        
        logger.info(f"Processing webhook event: {event}")
        
        # Nota: Chatwoot não oferece verificação de assinatura HMAC
        # Os webhooks são enviados sem secret token ou headers personalizados
        # A verificação de autenticidade deve ser feita por outros meios se necessário
        
        # Processar diferentes tipos de eventos
        if event == "message_created":
            await handle_message_created(payload)
        elif event == "message_updated":
            await handle_message_updated(payload)
        elif event == "conversation_created":
            await handle_conversation_created(payload)
        elif event == "conversation_updated":
            await handle_conversation_updated(payload)
        elif event == "conversation_status_changed":
            await handle_conversation_status_changed(payload)
        elif event == "contact_updated":
            await handle_contact_updated(payload)
        elif event == "conversation_typing_on":
            await handle_conversation_typing_on(payload)
        elif event == "conversation_typing_off":
            await handle_conversation_typing_off(payload)
        else:
            logger.warning(f"Unhandled webhook event: {event}")
        
        return {"status": "success", "event": event}
    
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def handle_message_created(data: Dict[str, Any]):
    """Processar mensagem criada"""
    try:
        # Preparar dados da mensagem
        message_data = data.copy()  # Fazer uma cópia para não modificar o original
        conversation_id = message_data.get("conversation", {}).get("id")
        
        # Processar áudio se houver
        audio_info = await media_handler.handle_audio(message_data)
        if audio_info:
            logger.info(f"✅ Áudio processado: {audio_info['filepath']}")
            # Adicionar URL do áudio à mensagem
            message_data["audio_url"] = audio_info["public_url"]
            logger.info(f"🔊 URL do áudio: {audio_info['public_url']}")
            
            # Garantir que a mensagem tenha conteúdo mesmo que seja apenas áudio
            if not message_data.get("content"):
                message_data["content"] = "🎵 Mensagem de áudio"
                
            # Garantir que o áudio esteja disponível no frontend
            if "attachments" in message_data:
                for attachment in message_data["attachments"]:
                    if attachment.get("file_type") == "audio":
                        attachment["local_url"] = audio_info["public_url"]
        
        # Processar imagens se houver (NOVA FUNCIONALIDADE)
        try:
            logger.info(f"🔍 Verificando attachments para processamento de imagens...")
            attachments = message_data.get("attachments", [])
            logger.info(f"📎 Total de attachments: {len(attachments)}")
            
            for i, attachment in enumerate(attachments):
                logger.info(f"📎 Attachment {i}: file_type='{attachment.get('file_type')}', extension='{attachment.get('extension')}'")
            
            image_attachments = await attachment_service.process_message_attachments(message_data)
            logger.info(f"🖼️ Imagens processadas: {len(image_attachments)}")
            
            if image_attachments:
                logger.info(f"✅ {len(image_attachments)} imagem(ns) processada(s)")
                # Adicionar metadados das imagens à mensagem
                message_data["image_attachments"] = [
                    {
                        "id": img.id,
                        "filename": img.filename,
                        "content_type": img.content_type,
                        "file_size": img.file_size,
                        "data_url": img.data_url
                    } for img in image_attachments
                ]
                
                # Garantir que a mensagem tenha conteúdo mesmo que seja apenas imagem
                if not message_data.get("content"):
                    message_data["content"] = "📷 Imagem enviada"
                    
                logger.info(f"🖼️ image_attachments adicionadas à mensagem: {len(message_data['image_attachments'])}")
            else:
                logger.info(f"❌ Nenhuma imagem processada")
        except Exception as e:
            logger.warning(f"Erro ao processar imagens: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Não falhar o webhook se houver erro no processamento de imagens
        
        # Emitir evento de nova mensagem via WebSocket com dados processados
        await ws_manager.emit_new_message(conversation_id, message_data)
        
        # Processar lógica de IA e salvar no banco
        conversation_data = message_data.get("conversation", {})
        logger.info(f"Processing message: {message_data.get('id')} from conversation: {conversation_data.get('id')}")
        
        # DEBUG: Log detalhado dos dados da mensagem
        logger.info(f"🔍 DEBUG - message_type: {message_data.get('message_type')}")
        logger.info(f"🔍 DEBUG - sender_type: {message_data.get('sender_type')}")
        logger.info(f"🔍 DEBUG - sender: {message_data.get('sender', {})}")
        logger.info(f"🔍 DEBUG - content: {message_data.get('content', '')[:100]}")
        
        # Verificar se é mensagem de usuário (não bot) e processar automaticamente com agente IA
        message_type = message_data.get("message_type")
        
        # O sender_type pode estar em diferentes lugares, vamos procurar
        sender_type = None
        
        # Primeiro, tentar no nível raiz da mensagem
        sender_type = message_data.get("sender_type")
        
        # Se não encontrou, tentar dentro de messages[0]
        if not sender_type:
            messages = message_data.get("messages", [])
            if messages and len(messages) > 0:
                sender_type = messages[0].get("sender_type")
        
        # Se ainda não encontrou, tentar dentro de conversation.messages[0]
        if not sender_type:
            conversation = message_data.get("conversation", {})
            messages = conversation.get("messages", [])
            if messages and len(messages) > 0:
                sender_type = messages[0].get("sender_type")
        
        logger.info(f"🔍 DEBUG - Condições: message_type='{message_type}' == 'incoming': {message_type == 'incoming'}")
        logger.info(f"🔍 DEBUG - Condições: sender_type='{sender_type}' == 'Contact': {sender_type == 'Contact'}")
        
        if message_type == "incoming" and sender_type == "Contact":
            content = message_data.get("content", "")
            
            logger.info(f"📨 Nova mensagem recebida: {content[:100]}...")
            
            # Verificar se agente está disponível
            if ai_agent.is_available():
                logger.info("🤖 Agente IA disponível - processando mensagem automaticamente")
                
                # Processar com IA
                ai_response = await process_with_ai(content, conversation_data)
                
                # Enviar resposta do agente para Chatwoot
                if ai_response:
                    await send_message_to_chatwoot(
                        conversation_data.get("id"),
                        ai_response,
                        message_data.get("account", {}).get("id"),
                        is_ai_agent=True
                    )
                    logger.info("✅ Resposta do agente enviada automaticamente")
            else:
                logger.warning("⚠️ Agente IA não disponível - mensagem não será respondida automaticamente")
        else:
            logger.info(f"🔍 DEBUG - Condição não atendida: message_type='{message_type}', sender_type='{sender_type}'")
        
        # Salvar no banco de dados
        await save_message_to_database(message_data, conversation_data)
        
    except Exception as e:
        logger.error(f"Error handling message created: {str(e)}")

async def handle_message_updated(data: Dict[str, Any]):
    """Processar mensagem atualizada"""
    try:
        message_data = data
        conversation_data = data.get("conversation", {})
        
        logger.info(f"Message updated: {message_data.get('id')} from conversation: {conversation_data.get('id')}")
        
        # Atualizar mensagem no banco de dados
        await update_message_in_database(message_data, conversation_data)
        
    except Exception as e:
        logger.error(f"Error handling message updated: {str(e)}")

async def handle_conversation_status_changed(data: Dict[str, Any]):
    """Processar mudança de status da conversa"""
    try:
        # O payload do Chatwoot vem diretamente com os dados da conversa
        conversation_data = data
        logger.info(f"Conversation status changed: {conversation_data.get('id')} to {conversation_data.get('status')}")
        
        # Atualizar status no banco de dados
        await update_conversation_status(conversation_data)
        
    except Exception as e:
        logger.error(f"Error handling conversation status change: {str(e)}")

async def handle_conversation_created(data: Dict[str, Any]):
    """Processar conversa criada"""
    try:
        # O payload do Chatwoot vem diretamente com os dados da conversa
        conversation_data = data
        logger.info(f"New conversation created: {conversation_data.get('id')}")
        
        # Salvar conversa no banco de dados
        await save_conversation_to_database(conversation_data)
        
    except Exception as e:
        logger.error(f"Error handling conversation created: {str(e)}")

async def handle_conversation_updated(data: Dict[str, Any]):
    """Processar conversa atualizada"""
    try:
        conversation_data = data
        logger.info(f"Conversation updated: {conversation_data.get('id')}")
        
        # Atualizar conversa no banco de dados
        await update_conversation_in_database(conversation_data)
        
    except Exception as e:
        logger.error(f"Error handling conversation updated: {str(e)}")

async def handle_contact_updated(data: Dict[str, Any]):
    """Processar contato atualizado"""
    try:
        contact_data = data
        logger.info(f"Contact updated: {contact_data.get('id')} - {contact_data.get('name')}")
        
        # Atualizar contato no banco de dados
        await update_contact_in_database(contact_data)
        
    except Exception as e:
        logger.error(f"Error handling contact updated: {str(e)}")

async def handle_conversation_typing_on(data: Dict[str, Any]):
    """Processar usuário digitando"""
    try:
        conversation_data = data.get("conversation", {})
        user_data = data.get("user", {})
        
        logger.info(f"User {user_data.get('name')} is typing in conversation {conversation_data.get('id')}")
        
        # Opcional: Implementar lógica para indicar que usuário está digitando
        # Por exemplo, atualizar status em tempo real
        
    except Exception as e:
        logger.error(f"Error handling conversation typing on: {str(e)}")

async def handle_conversation_typing_off(data: Dict[str, Any]):
    """Processar usuário parou de digitar"""
    try:
        conversation_data = data.get("conversation", {})
        user_data = data.get("user", {})
        
        logger.info(f"User {user_data.get('name')} stopped typing in conversation {conversation_data.get('id')}")
        
        # Opcional: Implementar lógica para indicar que usuário parou de digitar
        
    except Exception as e:
        logger.error(f"Error handling conversation typing off: {str(e)}")

async def process_with_ai(content: str, conversation_data: Dict[str, Any]) -> str:
    """Processar mensagem com IA usando o agente especializado"""
    try:
        conversation_id = conversation_data.get("id")
        contact_info = conversation_data.get("meta", {}).get("sender", {})
        
        logger.info(f"🤖 Agente processando mensagem da conversa {conversation_id}")
        
        # Usar o agente especializado
        ai_response = await ai_agent.process_message(
            message=content,
            conversation_id=conversation_id,
            contact_info=contact_info
        )
        
        if ai_response:
            logger.info(f"✅ Agente respondeu: {ai_response[:100]}...")
            return ai_response
        else:
            logger.warning("Agente não conseguiu gerar resposta")
            return "Olá! Recebi sua mensagem. Nossa equipe técnica irá respondê-lo em breve. Obrigado pelo contato! 😊"
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar com agente IA: {str(e)}")
        return "Olá! Recebi sua mensagem. Nossa equipe técnica irá respondê-lo em breve. Obrigado pelo contato! 😊"

async def send_message_to_chatwoot(conversation_id: int, content: str, account_id: int, is_ai_agent: bool = False):
    """Enviar mensagem para Chatwoot"""
    try:
        if not CHATWOOT_API_TOKEN or not CHATWOOT_URL:
            logger.warning("Chatwoot API not configured")
            return
        
        url = f"{CHATWOOT_URL}/api/v1/accounts/{account_id}/conversations/{conversation_id}/messages"
        
        headers = {
            "api_access_token": CHATWOOT_API_TOKEN,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Adicionar prefixo para identificar mensagens do agente
        if is_ai_agent:
            content = f"🤖 {content}"
        
        payload = {
            "content": content,
            "message_type": "outgoing"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
        agent_type = "Agente IA" if is_ai_agent else "Técnico"
        logger.info(f"✅ Mensagem enviada para Chatwoot conversa {conversation_id} ({agent_type})")
        
    except Exception as e:
        logger.error(f"❌ Erro ao enviar mensagem para Chatwoot: {str(e)}")

async def save_message_to_database(message_data: Dict[str, Any], conversation_data: Dict[str, Any]):
    """Salvar mensagem no banco de dados"""
    try:
        # TODO: Implementar salvamento no PostgreSQL
        logger.info(f"Saving message {message_data.get('id')} to database")
        
    except Exception as e:
        logger.error(f"Error saving message to database: {str(e)}")

async def save_conversation_to_database(conversation_data: Dict[str, Any]):
    """Salvar conversa no banco de dados"""
    try:
        # TODO: Implementar salvamento no PostgreSQL
        logger.info(f"Saving conversation {conversation_data.get('id')} to database")
        
    except Exception as e:
        logger.error(f"Error saving conversation to database: {str(e)}")

async def update_message_in_database(message_data: Dict[str, Any], conversation_data: Dict[str, Any]):
    """Atualizar mensagem no banco de dados"""
    try:
        # TODO: Implementar atualização no PostgreSQL
        logger.info(f"Updating message {message_data.get('id')} in database")
        
    except Exception as e:
        logger.error(f"Error updating message in database: {str(e)}")

async def update_conversation_in_database(conversation_data: Dict[str, Any]):
    """Atualizar conversa no banco de dados"""
    try:
        # TODO: Implementar atualização no PostgreSQL
        logger.info(f"Updating conversation {conversation_data.get('id')} in database")
        
    except Exception as e:
        logger.error(f"Error updating conversation in database: {str(e)}")

async def update_conversation_status(conversation_data: Dict[str, Any]):
    """Atualizar status da conversa no banco de dados"""
    try:
        # TODO: Implementar atualização no PostgreSQL
        logger.info(f"Updating conversation {conversation_data.get('id')} status")
        
    except Exception as e:
        logger.error(f"Error updating conversation status: {str(e)}")

async def update_contact_in_database(contact_data: Dict[str, Any]):
    """Atualizar contato no banco de dados"""
    try:
        # TODO: Implementar atualização no PostgreSQL
        logger.info(f"Updating contact {contact_data.get('id')} in database")
        
    except Exception as e:
        logger.error(f"Error updating contact in database: {str(e)}")

# Endpoint para testar webhook
@app.post("/webhook/test", tags=["Webhooks"])
async def test_webhook():
    """Endpoint para testar webhook"""
    return {
        "status": "success",
        "message": "Webhook endpoint is working",
        "timestamp": datetime.now().isoformat()
    }

# Endpoints para gerenciar webhooks do Chatwoot
@app.get("/webhooks", tags=["Chatwoot Management"])
async def list_webhooks():
    """Listar todos os webhooks configurados no Chatwoot"""
    try:
        if not CHATWOOT_API_TOKEN:
            raise HTTPException(status_code=400, detail="CHATWOOT_API_TOKEN not configured")
        
        # TODO: Implementar listagem de webhooks via API do Chatwoot
        # GET /api/v1/accounts/{account_id}/webhooks
        return {
            "status": "success",
            "message": "Webhook listing not implemented yet",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error listing webhooks: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/webhooks", tags=["Chatwoot Management"])
async def create_webhook(webhook_data: dict):
    """Criar novo webhook no Chatwoot"""
    try:
        if not CHATWOOT_API_TOKEN:
            raise HTTPException(status_code=400, detail="CHATWOOT_API_TOKEN not configured")
        
        # TODO: Implementar criação de webhook via API do Chatwoot
        # POST /api/v1/accounts/{account_id}/webhooks
        return {
            "status": "success",
            "message": "Webhook creation not implemented yet",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error creating webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/webhooks/{webhook_id}", tags=["Chatwoot Management"])
async def get_webhook(webhook_id: int):
    """Obter detalhes de um webhook específico"""
    try:
        if not CHATWOOT_API_TOKEN:
            raise HTTPException(status_code=400, detail="CHATWOOT_API_TOKEN not configured")
        
        # TODO: Implementar obtenção de webhook via API do Chatwoot
        return {
            "status": "success",
            "message": f"Webhook {webhook_id} details not implemented yet",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/webhooks/{webhook_id}", tags=["Chatwoot Management"])
async def delete_webhook(webhook_id: int):
    """Deletar webhook do Chatwoot"""
    try:
        if not CHATWOOT_API_TOKEN:
            raise HTTPException(status_code=400, detail="CHATWOOT_API_TOKEN not configured")
        
        # TODO: Implementar deleção de webhook via API do Chatwoot
        # DELETE /api/v1/accounts/{account_id}/webhooks/{webhook_id}
        return {
            "status": "success",
            "message": f"Webhook {webhook_id} deletion not implemented yet",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error deleting webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Endpoints para o frontend técnico
@app.get("/api/conversations", tags=["Frontend API"])
async def get_conversations():
    """Listar conversas para o painel técnico"""
    try:
        if not CHATWOOT_API_TOKEN:
            raise HTTPException(status_code=400, detail="CHATWOOT_API_TOKEN not configured")
        
        # Chamada real para API do Chatwoot
        url = f"{CHATWOOT_URL}/api/v1/accounts/{CHATWOOT_ACCOUNT_ID}/conversations"
        headers = {
            "api_access_token": CHATWOOT_API_TOKEN,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            # Extrair payload independentemente da versão
            payload = extract_chatwoot_payload(data)
            logger.info(f"Processing {len(payload)} conversations from Chatwoot")
            
            conversations = []
            for conv in payload:
                # Extrair dados do contato
                meta = conv.get("meta", {})
                sender = meta.get("sender", {})
                
                # Extrair última mensagem
                messages = conv.get("messages", [])
                last_message = "Sem mensagens"
                if messages:
                    last_msg = messages[-1]
                    last_message = last_msg.get("content", "Sem mensagens")
                
                conversation = {
                    "id": conv.get("id"),
                    "contact": {
                        "name": sender.get("name", "Usuário"),
                        "phone": sender.get("phone_number", "")
                    },
                    "lastMessage": last_message,
                    "timestamp": conv.get("last_activity_at", conv.get("updated_at")),
                    "status": conv.get("status", "open"),
                    "unreadCount": conv.get("unread_count", 0)
                }
                conversations.append(conversation)
            
            logger.info(f"Processed {len(conversations)} conversations for frontend")
            
            return {
                "status": "success",
                "conversations": conversations
            }
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Error getting conversations: {str(e)}\n{error_details}")
        
        # Log request details
        logger.error(f"Request URL: {url}")
        logger.error(f"Request headers: {headers}")
        
        # Retornar dados mockados em caso de erro
        return {
            "status": "success",
            "conversations": [
                {
                    "id": 1,
                    "contact": {
                        "name": "João Silva",
                        "phone": "+55 11 99999-9999"
                    },
                    "lastMessage": "Olá, preciso de ajuda com meu documento",
                    "timestamp": datetime.now().isoformat(),
                    "status": "open",
                    "unreadCount": 2
                }
            ],
            "message": f"Using mock data due to error: {str(e)}\nURL: {url}"
        }

@app.get("/api/conversations/{conversation_id}/messages", tags=["Frontend API"])
async def get_conversation_messages(
    conversation_id: int,
    since: Optional[int] = None  # timestamp para buscar apenas mensagens novas
):
    """Obter mensagens de uma conversa específica
    
    - conversation_id: ID da conversa
    - since: Timestamp da última mensagem (opcional)
    """
    try:
        if not CHATWOOT_API_TOKEN:
            raise HTTPException(status_code=400, detail="CHATWOOT_API_TOKEN not configured")
        
        # Chamada real para API do Chatwoot
        url = f"{CHATWOOT_URL}/api/v1/accounts/{CHATWOOT_ACCOUNT_ID}/conversations/{conversation_id}/messages"
        headers = {
            "api_access_token": CHATWOOT_API_TOKEN,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # Processar mensagens para o frontend (inclui áudio e imagens)
            messages: List[Dict[str, Any]] = []
            for msg in extract_chatwoot_payload(data):
                content = msg.get("content") or ""
                # Mapear remetente
                sender = "user" if msg.get("message_type") == 1 else "contact"

                # Detectar áudio nos attachments
                audio_url: Optional[str] = None
                attachments = msg.get("attachments", [])
                audio_attachment = next((a for a in attachments if a.get("file_type") == "audio"), None)
                if audio_attachment:
                    # Tentar URL local salva previamente (via webhook) ou fallback para data_url do Chatwoot
                    audio_url = audio_attachment.get("local_url") or audio_attachment.get("data_url")
                    # Se não há content, exibir rótulo amigável
                    if not content:
                        content = "🎵 Mensagem de áudio"

                # Processar imagens nos attachments (NOVA FUNCIONALIDADE)
                image_attachments = []
                try:
                    logger.info(f"🔍 API: Verificando attachments para mensagem {msg.get('id')}: {len(attachments)} attachments")
                    
                    # Criar uma mensagem temporária para processar imagens
                    temp_message = {
                        "attachments": attachments,
                        "id": msg.get("id"),
                        "conversation_id": conversation_id
                    }
                    
                    # Processar imagens usando o attachment_service
                    processed_images = await attachment_service.process_message_attachments(temp_message)
                    logger.info(f"🖼️ API: Processadas {len(processed_images)} imagens para mensagem {msg.get('id')}")
                    
                    if processed_images:
                        image_attachments = [
                            {
                                "id": img.id,
                                "filename": img.filename,
                                "content_type": img.content_type,
                                "file_size": img.file_size,
                                "data_url": img.data_url
                            } for img in processed_images
                        ]
                        
                        # Se não há content, exibir rótulo amigável
                        if not content:
                            content = "📷 Imagem enviada"
                            
                        logger.info(f"✅ API: Adicionadas {len(image_attachments)} image_attachments para mensagem {msg.get('id')}")
                    else:
                        logger.info(f"❌ API: Nenhuma imagem processada para mensagem {msg.get('id')}")
                except Exception as e:
                    logger.warning(f"Erro ao processar imagens na API: {e}")
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    # Não falhar se houver erro no processamento de imagens

                message = {
                    "id": msg.get("id"),
                    "conversation_id": conversation_id,
                    "content": content,
                    "sender": sender,
                    "timestamp": msg.get("created_at"),
                    "status": msg.get("status", "sent"),
                    "audio_url": audio_url,
                    "attachments": attachments,
                    "image_attachments": image_attachments,  # NOVA FUNCIONALIDADE
                }
                messages.append(message)
            
            return {
                "status": "success",
                "messages": messages
            }
        
    except Exception as e:
        logger.error(f"Error getting messages: {str(e)}")
        # Retornar dados mockados em caso de erro
        return {
            "status": "success",
            "messages": [
                {
                    "id": 1,
                    "content": "Olá, preciso de ajuda com meu documento",
                    "sender": "contact",
                    "timestamp": datetime.now().isoformat(),
                    "status": "sent"
                },
                {
                    "id": 2,
                    "content": "Olá! Como posso ajudá-lo?",
                    "sender": "user",
                    "timestamp": datetime.now().isoformat(),
                    "status": "sent"
                }
            ],
            "message": f"Using mock data due to error: {str(e)}"
        }

@app.post("/api/conversations/{conversation_id}/messages", tags=["Frontend API"])
async def send_message_to_conversation(conversation_id: int, message_data: dict):
    """Enviar mensagem para uma conversa"""
    try:
        if not CHATWOOT_API_TOKEN:
            raise HTTPException(status_code=400, detail="CHATWOOT_API_TOKEN not configured")
        
        content = message_data.get("content", "")
        if not content:
            raise HTTPException(status_code=400, detail="Content is required")
        
        # Chamada real para API do Chatwoot
        url = f"{CHATWOOT_URL}/api/v1/accounts/{CHATWOOT_ACCOUNT_ID}/conversations/{conversation_id}/messages"
        headers = {
            "api_access_token": CHATWOOT_API_TOKEN,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        payload = {
            "content": content,
            "message_type": "outgoing"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Message sent to conversation {conversation_id}: {content}")
            
            return {
                "status": "success",
                "message": "Message sent successfully",
                "message_id": data.get("id", 123)
            }
        
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/conversations/{conversation_id}/voice", tags=["Frontend API"])
async def send_voice_message(
    conversation_id: int,
    file: UploadFile = File(...),
    content: Optional[str] = Form("")
):
    """Enviar mensagem de áudio para a conversa via Chatwoot."""
    try:
        if not CHATWOOT_API_TOKEN or not CHATWOOT_URL:
            raise HTTPException(status_code=400, detail="Chatwoot not configured")

        # Montar request multipart para Chatwoot
        url = f"{CHATWOOT_URL}/api/v1/accounts/{CHATWOOT_ACCOUNT_ID}/conversations/{conversation_id}/messages"
        headers = {
            "api_access_token": CHATWOOT_API_TOKEN,
        }

        file_bytes = await file.read()
        filename = file.filename or "voice_message.ogg"
        mime = file.content_type or "audio/ogg"

        # Converter webm para MP3 diretamente (mais compatível com WhatsApp)
        try:
            if "webm" in (mime or "") or (filename or "").endswith(".webm"):
                import tempfile
                import subprocess
                import os
                
                logger.info("Convertendo áudio de webm para MP3 (compatibilidade WhatsApp)")
                
                # Criar arquivos temporários
                with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp_input:
                    temp_input.write(file_bytes)
                    temp_input.flush()
                    
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_output:
                    temp_output_path = temp_output.name
                    temp_output.close()
                
                # Converter usando ffmpeg com configurações específicas para WhatsApp MP3
                subprocess.run([
                    "ffmpeg", "-y", "-i", temp_input.name,
                    "-c:a", "libmp3lame", 
                    "-b:a", "32k",        # Bitrate baixo para WhatsApp
                    "-ar", "16000",       # Sample rate específico para WhatsApp
                    "-ac", "1",           # Mono
                    "-q:a", "9",          # Qualidade máxima (menor bitrate)
                    "-af", "highpass=f=80,lowpass=f=8000",  # Filtros para voz
                    temp_output_path
                ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                # Ler arquivo convertido
                with open(temp_output_path, "rb") as f:
                    file_bytes = f.read()
                
                # Atualizar filename e mime
                filename = (filename.rsplit('.', 1)[0] if '.' in filename else filename) + ".mp3"
                mime = "audio/mpeg"
                
                # Limpar arquivos temporários
                os.unlink(temp_input.name)
                os.unlink(temp_output_path)
                
                logger.info(f"Conversão MP3 concluída: {filename}, {mime}, {len(file_bytes)} bytes")
                
                # Verificar se o arquivo não é muito grande para WhatsApp (16MB limite)
                if len(file_bytes) > 16 * 1024 * 1024:  # 16MB
                    logger.warning(f"Arquivo MP3 muito grande ({len(file_bytes)} bytes), reduzindo qualidade")
                    
                    # Tentar MP3 com qualidade ainda menor
                    mp3_low_output = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
                    mp3_low_path = mp3_low_output.name
                    mp3_low_output.close()
                    
                    subprocess.run([
                        "ffmpeg", "-y", "-i", temp_input.name,
                        "-c:a", "libmp3lame", "-b:a", "16k",
                        "-ar", "8000", "-ac", "1",
                        mp3_low_path
                    ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    
                    with open(mp3_low_path, "rb") as f:
                        file_bytes = f.read()
                    
                    filename = (filename.rsplit('.', 1)[0] if '.' in filename else filename) + "_low.mp3"
                    mime = "audio/mpeg"
                    os.unlink(mp3_low_path)
                    
                    logger.info(f"MP3 baixa qualidade: {filename}, {mime}, {len(file_bytes)} bytes")
                
        except Exception as e:
            logger.warning(f"Falha ao converter áudio para MP3: {e}")
            # Continuar com arquivo original se conversão falhar

        data = {
            "message_type": "outgoing",
            "content": content or "",
        }

        # Para WhatsApp via Chatwoot, aceitam-se formatos como audio/ogg ou audio/mpeg
        # Alguns provedores exigem campo 'attachments[]' e 'message_type=outgoing'
        files = {
            'attachments[]': (filename, file_bytes, mime)
        }

        async with httpx.AsyncClient() as client:
            logger.info(f"Enviando áudio para Chatwoot: {url}")
            logger.info(f"Headers: {headers}")
            logger.info(f"Data: {data}")
            logger.info(f"File: {filename}, MIME: {mime}, Size: {len(file_bytes)} bytes")
            
            resp = await client.post(url, headers=headers, data=data, files=files)
            logger.info(f"Response status: {resp.status_code}")
            logger.info(f"Response headers: {dict(resp.headers)}")
            
            resp.raise_for_status()
            result = resp.json()
            logger.info(f"Chatwoot response: {result}")

        return {
            "status": "success",
            "message": "Voice message sent",
            "payload": result
        }

    except httpx.HTTPStatusError as e:
        logger.error(f"Chatwoot HTTP error: {e.response.status_code} {e.response.text[:200]}")
        raise HTTPException(status_code=502, detail="Chatwoot API error")
    except Exception as e:
        logger.error(f"Error sending voice message: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/conversations/{conversation_id}/image", tags=["Messages"], response_model=ImageUploadResponse)
async def send_image_message(
    conversation_id: int,
    file: UploadFile = File(...),
    content: str = Form("")
):
    """Enviar imagem para uma conversa via Chatwoot"""
    try:
        # Validar se é uma imagem
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Arquivo deve ser uma imagem")
        
        # Ler arquivo
        file_bytes = await file.read()
        
        # Validar tamanho (máximo 10MB)
        if len(file_bytes) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Arquivo muito grande (máximo 10MB)")
        
        logger.info(f"Enviando imagem: {file.filename} ({len(file_bytes)} bytes)")
        
        # Enviar para Chatwoot
        result = await attachment_service.upload_image_to_chatwoot(
            conversation_id=conversation_id,
            file_bytes=file_bytes,
            filename=file.filename,
            content_type=file.content_type,
            content=content
        )
        
        # Emitir evento via WebSocket
        await ws_manager.emit_new_message(conversation_id, {
            "id": result.get("id"),
            "content": content or "📷 Imagem enviada",
            "conversation_id": conversation_id,
            "message_type": "outgoing",
            "sender": {"name": "Sistema"},
            "created_at": datetime.now().isoformat(),
            "image_attachments": [{
                "id": attachment.get("id"),
                "filename": attachment.get("extension"),
                "content_type": attachment.get("file_type"),
                "file_size": attachment.get("file_size"),
                "data_url": attachment.get("data_url")
            } for attachment in result.get("attachments", [])]
        })
        
        return ImageUploadResponse(
            status="success",
            message="Imagem enviada com sucesso",
            attachment_id=result.get("attachments", [{}])[0].get("id") if result.get("attachments") else None,
            message_id=result.get("id")
        )
        
    except Exception as e:
        logger.error(f"Error sending image: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Endpoint de debug para verificar dados da API
@app.get("/debug/conversations", tags=["Debug"])
async def debug_conversations():
    """Endpoint de debug para verificar dados da API do Chatwoot"""
    try:
        if not CHATWOOT_API_TOKEN:
            return {"error": "CHATWOOT_API_TOKEN not configured"}
        
        url = f"{CHATWOOT_URL}/api/v1/accounts/{CHATWOOT_ACCOUNT_ID}/conversations"
        headers = {
            "api_access_token": CHATWOOT_API_TOKEN,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            return {
                "status": "success",
                "raw_data": data,
                "conversations_count": len(data.get("payload", [])),
                "first_conversation": data.get("payload", [{}])[0] if data.get("payload") else None
            }
        
    except Exception as e:
        return {"error": str(e), "url": url}

@app.post("/api/agent/test", tags=["AI Agent"])
async def test_agent(message_data: dict):
    """Endpoint temporário para testar o agente IA"""
    try:
        message = message_data.get("message", "")
        conversation_id = message_data.get("conversation_id", 1)
        contact_info = message_data.get("contact_info", {})
        
        logger.info(f"🧪 Testando agente com mensagem: {message}")
        
        # Verificar se agente está disponível
        if not ai_agent.is_available():
            return {"status": "error", "message": "Agente não disponível"}
        
        # Processar com IA
        ai_response = await ai_agent.process_message(
            message=message,
            conversation_id=conversation_id,
            contact_info=contact_info
        )
        
        return {
            "status": "success",
            "message": message,
            "ai_response": ai_response,
            "conversation_id": conversation_id
        }
        
    except Exception as e:
        logger.error(f"Erro no teste do agente: {str(e)}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)