"""
Handler para download e armazenamento de mídia do Chatwoot
"""
import os
import logging
import httpx
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class MediaHandler:
    def __init__(self):
        """Inicializar handler de mídia"""
        self.media_dir = os.path.join(os.path.dirname(__file__), '..', 'media', 'audio')
        os.makedirs(self.media_dir, exist_ok=True)
        logger.info(f"📂 Diretório de mídia: {self.media_dir}")

    async def handle_audio(self, message_data: Dict[str, Any]) -> Optional[str]:
        """Processar áudio do WhatsApp
        
        Args:
            message_data: Dados da mensagem do webhook
            
        Returns:
            Optional[str]: Caminho do arquivo salvo ou None se falhar
        """
        try:
            # Verificar se é mensagem do cliente
            if message_data.get("message_type") != "incoming":
                return None

            # Verificar attachments
            attachments = message_data.get("attachments", [])
            if not attachments:
                return None

            # Procurar áudio nos attachments
            audio_attachment = None
            for attachment in attachments:
                if attachment.get("file_type") == "audio":
                    audio_attachment = attachment
                    break

            if not audio_attachment:
                return None

            # Extrair dados do áudio
            extension = "ogg"  # Chatwoot sempre envia áudio como OGG
            download_url = audio_attachment.get("data_url")

            if not download_url:
                logger.error("❌ URL de download não encontrada")
                return None

            # Gerar nome único
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            conversation_id = message_data.get("conversation_id", "unknown")
            message_id = message_data.get("id", "unknown")
            filename = f"audio_{conversation_id}_{message_id}_{timestamp}.{extension}"
            filepath = os.path.join(self.media_dir, filename)
            
            # Gerar URL pública
            public_url = f"/media/audio/{filename}"
            
            # Baixar áudio
            logger.info(f"⬇️ Baixando áudio: {download_url}")
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(download_url)
                if response.status_code == 200:
                    # Salvar arquivo
                    with open(filepath, "wb") as f:
                        f.write(response.content)
                    logger.info(f"✅ Áudio salvo em: {filepath}")
                    return {
                        "filepath": filepath,
                        "public_url": public_url,
                        "filename": filename
                    }
                else:
                    logger.error(f"❌ Erro ao baixar áudio: {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"❌ Erro ao processar áudio: {str(e)}")
            return None

# Criar instância global
media_handler = MediaHandler()
