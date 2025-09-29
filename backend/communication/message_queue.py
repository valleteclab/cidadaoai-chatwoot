"""
Fila de mensagens para comunicação entre agentes
"""
import asyncio
import logging
from typing import Dict, List, Optional
from collections import deque
from datetime import datetime
from ..agents.base_agent import AgentMessage

logger = logging.getLogger(__name__)

class MessageQueue:
    """Fila de mensagens para comunicação entre agentes"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.queues: Dict[str, deque] = {}  # Fila por agente
        self.locks: Dict[str, asyncio.Lock] = {}  # Lock por agente
        self.subscribers: Dict[str, List[callable]] = {}  # Callbacks por evento
        
        logger.info(f"📬 MessageQueue inicializada (max_size={max_size})")
    
    async def _get_queue_lock(self, agent_id: str) -> asyncio.Lock:
        """Obter lock para fila do agente"""
        if agent_id not in self.locks:
            self.locks[agent_id] = asyncio.Lock()
        return self.locks[agent_id]
    
    async def enqueue(self, message: AgentMessage):
        """Adicionar mensagem à fila"""
        async with await self._get_queue_lock(message.to_agent):
            if message.to_agent not in self.queues:
                self.queues[message.to_agent] = deque()
            
            # Verificar tamanho máximo
            if len(self.queues[message.to_agent]) >= self.max_size:
                # Remover mensagem mais antiga
                self.queues[message.to_agent].popleft()
                logger.warning(f"⚠️ Fila do agente {message.to_agent} cheia, removendo mensagem antiga")
            
            self.queues[message.to_agent].append(message)
            
            logger.info(f"📨 Mensagem enfileirada: {message.from_agent} → {message.to_agent} ({message.event})")
            
            # Notificar subscribers
            await self._notify_subscribers(message)
    
    async def dequeue(self, agent_id: str) -> Optional[AgentMessage]:
        """Remover e retornar próxima mensagem da fila"""
        async with await self._get_queue_lock(agent_id):
            if agent_id not in self.queues or not self.queues[agent_id]:
                return None
            
            message = self.queues[agent_id].popleft()
            logger.info(f"📤 Mensagem desenfileirada: {agent_id} recebeu {message.event} de {message.from_agent}")
            return message
    
    async def peek(self, agent_id: str) -> Optional[AgentMessage]:
        """Ver próxima mensagem sem remover da fila"""
        async with await self._get_queue_lock(agent_id):
            if agent_id not in self.queues or not self.queues[agent_id]:
                return None
            
            return self.queues[agent_id][0]
    
    def get_queue_size(self, agent_id: str) -> int:
        """Obter tamanho da fila do agente"""
        return len(self.queues.get(agent_id, []))
    
    def get_all_queue_sizes(self) -> Dict[str, int]:
        """Obter tamanho de todas as filas"""
        return {agent_id: len(queue) for agent_id, queue in self.queues.items()}
    
    async def subscribe(self, event_type: str, callback: callable):
        """Inscrever callback para evento específico"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        self.subscribers[event_type].append(callback)
        logger.info(f"📡 Callback inscrito para evento: {event_type}")
    
    async def _notify_subscribers(self, message: AgentMessage):
        """Notificar subscribers sobre nova mensagem"""
        if message.event in self.subscribers:
            for callback in self.subscribers[message.event]:
                try:
                    await callback(message)
                except Exception as e:
                    logger.error(f"❌ Erro ao notificar subscriber: {e}")
    
    def clear_queue(self, agent_id: str):
        """Limpar fila do agente"""
        if agent_id in self.queues:
            self.queues[agent_id].clear()
            logger.info(f"🗑️ Fila do agente {agent_id} limpa")
    
    def clear_all_queues(self):
        """Limpar todas as filas"""
        for agent_id in list(self.queues.keys()):
            self.clear_queue(agent_id)
        logger.info("🗑️ Todas as filas limpas")
    
    def get_stats(self) -> Dict[str, any]:
        """Obter estatísticas das filas"""
        return {
            'total_agents': len(self.queues),
            'queue_sizes': self.get_all_queue_sizes(),
            'total_messages': sum(len(queue) for queue in self.queues.values()),
            'subscribers': {event: len(callbacks) for event, callbacks in self.subscribers.items()}
        }
