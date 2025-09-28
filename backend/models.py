"""
Modelos de dados para o Cidadão.AI Chatwoot
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from decimal import Decimal


class ChatwootAttachment(BaseModel):
    """Modelo para metadados de attachments do Chatwoot"""
    
    id: int                           # ID do attachment no Chatwoot
    message_id: int                   # ID da mensagem no Chatwoot
    conversation_id: Optional[int] = None  # ID da conversa (opcional)
    filename: Optional[str] = None    # Nome original do arquivo
    content_type: Optional[str] = None # MIME type (image/jpeg, image/png, etc)
    file_size: Optional[int] = None   # Tamanho em bytes
    blob_key: Optional[str] = None    # Chave do blob no Chatwoot
    data_url: Optional[str] = None    # URL do arquivo no Chatwoot
    created_at: Optional[datetime] = None  # Timestamp de criação (opcional)
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


# ========================================
# MODELOS DO SISTEMA DE CHAMADOS
# ========================================

class Prefeitura(BaseModel):
    """Modelo para Prefeituras/Clientes"""
    
    id: Optional[int] = None
    nome: str
    chatwoot_account_id: Optional[int] = None
    chatwoot_inbox_id: Optional[int] = None
    whatsapp_number: Optional[str] = None
    config: Dict[str, Any] = {}
    active: bool = True
    created_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Time(BaseModel):
    """Modelo para Times/Secretarias"""
    
    id: Optional[int] = None
    prefeitura_id: int
    nome: str
    chatwoot_team_id: Optional[int] = None
    cor: str = "#4ECDC4"
    keywords: List[str] = []
    responsavel_nome: Optional[str] = None
    responsavel_email: Optional[str] = None
    config: Dict[str, Any] = {}
    active: bool = True
    created_at: Optional[datetime] = None


class Agente(BaseModel):
    """Modelo para Agentes (Humanos e IA)"""
    
    id: Optional[int] = None
    prefeitura_id: int
    nome: str
    tipo: str  # 'humano', 'ia_cadastro', 'ia_infraestrutura', 'ia_geral', etc.
    chatwoot_agent_id: Optional[int] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    config: Dict[str, Any] = {}
    active: bool = True
    created_at: Optional[datetime] = None


class AgenteTime(BaseModel):
    """Modelo para relacionamento Agente-Time"""
    
    id: Optional[int] = None
    agente_id: int
    time_id: int
    role: str = "member"  # 'member', 'admin'
    created_at: Optional[datetime] = None


class Cidadao(BaseModel):
    """Modelo para Cidadãos"""
    
    id: Optional[int] = None
    prefeitura_id: int
    nome: str
    cpf: Optional[str] = None
    telefone: str
    email: Optional[str] = None
    endereco: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    cep: Optional[str] = None
    chatwoot_contact_id: Optional[int] = None
    data_nascimento: Optional[datetime] = None
    genero: Optional[str] = None
    config: Dict[str, Any] = {}
    active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CategoriaChamado(BaseModel):
    """Modelo para Categorias de Chamados"""
    
    id: Optional[int] = None
    prefeitura_id: int
    time_id: int
    nome: str
    descricao: Optional[str] = None
    keywords: List[str] = []
    prioridade: str = "normal"  # 'baixa', 'normal', 'alta', 'urgente'
    sla_horas: int = 72
    template_resposta: Optional[str] = None
    active: bool = True
    created_at: Optional[datetime] = None


class Chamado(BaseModel):
    """Modelo para Chamados/Protocolos"""
    
    id: Optional[int] = None
    prefeitura_id: int
    protocolo: str
    cidadao_id: int
    categoria_id: Optional[int] = None
    time_id: Optional[int] = None
    chatwoot_conversation_id: Optional[int] = None
    
    # Dados do chamado
    titulo: str
    descricao: str
    endereco_ocorrencia: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    
    # Status e fluxo
    status: str = "aberto"  # 'aberto', 'em_andamento', 'resolvido', 'cancelado'
    prioridade: str = "normal"  # 'baixa', 'normal', 'alta', 'urgente'
    sla_deadline: Optional[datetime] = None
    
    # Atribuições
    agente_responsavel_id: Optional[int] = None
    agente_atribuido_por_id: Optional[int] = None
    
    # Metadados
    fonte: str = "whatsapp"  # 'whatsapp', 'web', 'telefone', 'presencial'
    tags: List[str] = []
    anexos: List[Dict[str, Any]] = []
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Configurações
    config: Dict[str, Any] = {}


class InteracaoChamado(BaseModel):
    """Modelo para Interações/Histórico do Chamado"""
    
    id: Optional[int] = None
    chamado_id: int
    agente_id: Optional[int] = None
    tipo: str  # 'mensagem', 'atribuicao', 'status_change', 'comentario', 'resolucao'
    conteudo: str
    metadata: Dict[str, Any] = {}
    created_at: Optional[datetime] = None


class TemplateResposta(BaseModel):
    """Modelo para Templates de Resposta"""
    
    id: Optional[int] = None
    prefeitura_id: int
    categoria_id: Optional[int] = None
    nome: str
    template: str
    variaveis: Dict[str, Any] = {}
    active: bool = True
    created_at: Optional[datetime] = None


class ConfigIA(BaseModel):
    """Modelo para Configurações de IA"""
    
    id: Optional[int] = None
    prefeitura_id: int
    agente_id: int
    nome: str
    prompt_system: Optional[str] = None
    config: Dict[str, Any] = {}
    active: bool = True
    created_at: Optional[datetime] = None


# ========================================
# MODELOS DE REQUEST/RESPONSE
# ========================================

class CriarChamadoRequest(BaseModel):
    """Request para criar novo chamado"""
    
    cidadao_telefone: str
    titulo: str
    descricao: str
    endereco_ocorrencia: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    fonte: str = "whatsapp"


class CriarChamadoResponse(BaseModel):
    """Response para criação de chamado"""
    
    status: str
    chamado: Optional[Chamado] = None
    protocolo: Optional[str] = None
    message: str


class CadastrarCidadaoRequest(BaseModel):
    """Request para cadastrar cidadão"""
    
    telefone: str
    nome: str
    cpf: Optional[str] = None
    email: Optional[str] = None
    endereco: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    cep: Optional[str] = None
    data_nascimento: Optional[datetime] = None
    genero: Optional[str] = None


class CadastrarCidadaoResponse(BaseModel):
    """Response para cadastro de cidadão"""
    
    status: str
    cidadao: Optional[Cidadao] = None
    message: str


class ConsultarChamadoRequest(BaseModel):
    """Request para consultar chamado"""
    
    protocolo: Optional[str] = None
    telefone_cidadao: Optional[str] = None


class ConsultarChamadoResponse(BaseModel):
    """Response para consulta de chamado"""
    
    status: str
    chamado: Optional[Chamado] = None
    cidadao: Optional[Cidadao] = None
    categoria: Optional[CategoriaChamado] = None
    time: Optional[Time] = None
    message: str
