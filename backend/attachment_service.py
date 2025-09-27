"""
Service para gerenciar attachments do Chatwoot
"""
import os
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import httpx
from .models import ChatwootAttachment

logger = logging.getLogger(__name__)


class AttachmentService:
    """Service para gerenciar attachments de imagens do Chatwoot"""
    
    def __init__(self):
        self.chatwoot_url = os.getenv("CHATWOOT_URL")
        self.chatwoot_token = os.getenv("CHATWOOT_API_TOKEN")
        self.account_id = os.getenv("CHATWOOT_ACCOUNT_ID", "1")
    
    async def process_message_attachments(self, message_data: Dict[str, Any]) -> List[ChatwootAttachment]:
        """
        Processa attachments de uma mensagem do webhook
        """
        attachments = []
        
        # Verificar se a mensagem tem attachments
        message_attachments = message_data.get("attachments", [])
        if not message_attachments:
            return attachments
        
        logger.info(f"Processando {len(message_attachments)} attachments da mensagem {message_data.get('id')}")
        
        for attachment_data in message_attachments:
            logger.info(f"Processando attachment: {attachment_data}")
            
            # Só processar se for imagem
            if not self._is_image_attachment(attachment_data):
                logger.info(f"Pulando attachment (não é imagem): {attachment_data.get('file_type')}")
                continue
                
            attachment = ChatwootAttachment(
                id=attachment_data.get("id"),
                message_id=attachment_data.get("message_id"),
                conversation_id=message_data.get("conversation", {}).get("id"),
                filename=attachment_data.get("extension") or "image.jpg",  # Fallback se extension for None
                content_type=attachment_data.get("file_type") or "image/jpeg",  # Fallback se file_type for None
                file_size=attachment_data.get("file_size"),
                blob_key=None,  # Será extraído da data_url se necessário
                data_url=attachment_data.get("data_url"),
                created_at=datetime.now(),
                updated_at=None
            )
            
            attachments.append(attachment)
            logger.info(f"✅ Attachment processado: {attachment.filename} ({attachment.content_type}) - URL: {attachment.data_url}")
        
        return attachments
    
    def _is_image_attachment(self, attachment_data: Dict[str, Any]) -> bool:
        """Verifica se o attachment é uma imagem"""
        file_type = attachment_data.get("file_type", "")
        filename = attachment_data.get("extension", "")
        
        # Garantir que não sejam None
        file_type = file_type or ""
        filename = filename or ""
        
        logger.info(f"Verificando attachment: file_type='{file_type}', filename='{filename}', data={attachment_data}")
        
        # Verificar por tipo MIME
        if file_type.lower().startswith("image/"):
            logger.info(f"✅ Attachment detectado como imagem por MIME: {file_type}")
            return True
        
        # Verificar por extensão de arquivo (só se filename não for vazio)
        if filename:
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
            if any(filename.lower().endswith(ext) for ext in image_extensions):
                logger.info(f"✅ Attachment detectado como imagem por extensão: {filename}")
                return True
        
        logger.info(f"❌ Attachment não é imagem: {file_type} / {filename}")
        return False
    
    async def upload_image_to_chatwoot(
        self, 
        conversation_id: int, 
        file_bytes: bytes, 
        filename: str, 
        content_type: str,
        content: str = ""
    ) -> Dict[str, Any]:
        """
        Envia uma imagem para o Chatwoot via API
        """
        url = f"{self.chatwoot_url}/api/v1/accounts/{self.account_id}/conversations/{conversation_id}/messages"
        
        headers = {
            "api_access_token": self.chatwoot_token,
        }
        
        # Preparar dados do multipart
        data = {
            "message_type": "outgoing",
            "content": content or "📷 Imagem enviada",
        }
        
        files = {
            "attachments[]": (filename, file_bytes, content_type)
        }
        
        logger.info(f"Enviando imagem para Chatwoot: {filename} ({len(file_bytes)} bytes)")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=data, files=files)
            
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response headers: {dict(response.headers)}")
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Chatwoot response: {result}")
            
            return result
    
    async def get_signed_url(self, attachment: ChatwootAttachment) -> Optional[str]:
        """
        Gera uma URL assinada para o attachment (se necessário)
        Por enquanto, retorna a data_url diretamente do Chatwoot
        """
        if attachment.data_url:
            return attachment.data_url
        
        # Se não tiver data_url, tentar buscar do Chatwoot
        # (implementação futura se necessário)
        logger.warning(f"Attachment {attachment.id} não possui data_url")
        return None
    
    def get_thumbnail_url(self, attachment: ChatwootAttachment) -> Optional[str]:
        """
        Gera URL para thumbnail (se disponível)
        Por enquanto, retorna a URL normal
        """
        return self.get_signed_url(attachment)
