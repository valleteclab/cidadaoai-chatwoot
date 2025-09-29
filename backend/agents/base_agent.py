"""
Classe base para todos os agentes do sistema multi-agente
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AgentMessage:
    """Estrutura padrão para comunicação entre agentes"""
    event: str
    from_agent: str
    to_agent: str
    conversation_id: int
    data: Dict[str, Any]
    timestamp: datetime
    priority: int = 0
    retry_count: int = 0

class BaseAgent(ABC):
    """Classe base para todos os agentes especializados"""
    
    def __init__(self, agent_id: str, agent_name: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.is_active = True
        self.metrics = {
            'messages_processed': 0,
            'successful_responses': 0,
            'failed_responses': 0,
            'average_response_time': 0.0,
            'last_activity': None
        }
        
        logger.info(f"🤖 Agente {self.agent_name} ({self.agent_type}) inicializado")
    
    @abstractmethod
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """
        Processar mensagem recebida de outro agente
        
        Args:
            message: Mensagem recebida
            
        Returns:
            Resposta do agente ou None se não houver resposta
        """
        pass
    
    @abstractmethod
    async def handle_event(self, event: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Manipular evento específico do agente
        
        Args:
            event: Tipo do evento
            data: Dados do evento
            
        Returns:
            Resultado do processamento ou None
        """
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Obter status atual do agente"""
        return {
            'agent_id': self.agent_id,
            'agent_name': self.agent_name,
            'agent_type': self.agent_type,
            'is_active': self.is_active,
            'metrics': self.metrics.copy()
        }
    
    def update_metrics(self, response_time: float, success: bool):
        """Atualizar métricas do agente"""
        self.metrics['messages_processed'] += 1
        self.metrics['last_activity'] = datetime.now().isoformat()
        
        if success:
            self.metrics['successful_responses'] += 1
        else:
            self.metrics['failed_responses'] += 1
        
        # Calcular tempo médio de resposta
        total_responses = self.metrics['successful_responses'] + self.metrics['failed_responses']
        if total_responses > 0:
            current_avg = self.metrics['average_response_time']
            self.metrics['average_response_time'] = (
                (current_avg * (total_responses - 1) + response_time) / total_responses
            )
    
    def deactivate(self):
        """Desativar agente"""
        self.is_active = False
        logger.warning(f"⚠️ Agente {self.agent_name} desativado")
    
    def activate(self):
        """Ativar agente"""
        self.is_active = True
        logger.info(f"✅ Agente {self.agent_name} ativado")
    
    def __str__(self) -> str:
        return f"Agent({self.agent_name}, {self.agent_type}, active={self.is_active})"
