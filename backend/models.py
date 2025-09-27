"""
Modelos de dados para o Cidadão.AI Chatwoot
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ChatwootAttachment(BaseModel):
    """Modelo para metadados de attachments do Chatwoot"""
    
    id: int                           # ID do attachment no Chatwoot
    message_id: int                   # ID da mensagem no Chatwoot
    conversation_id: int              # ID da conversa
    filename: Optional[str] = None    # Nome original do arquivo
    content_type: Optional[str] = None # MIME type (image/jpeg, image/png, etc)
    file_size: Optional[int] = None   # Tamanho em bytes
    blob_key: Optional[str] = None    # Chave do blob no Chatwoot
    data_url: Optional[str] = None    # URL do arquivo no Chatwoot
    created_at: datetime              # Timestamp de criação
    updated_at: Optional[datetime] = None  # Timestamp de atualização
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ImageUploadRequest(BaseModel):
    """Modelo para requisição de upload de imagem"""
    
    conversation_id: int
    content: Optional[str] = ""  # Texto opcional junto com a imagem


class ImageUploadResponse(BaseModel):
    """Modelo para resposta de upload de imagem"""
    
    status: str
    message: str
    attachment_id: Optional[int] = None
    message_id: Optional[int] = None
