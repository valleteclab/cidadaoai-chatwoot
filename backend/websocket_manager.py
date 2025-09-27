"""
WebSocket Manager para atualizações em tempo real
"""
import socketio
import logging
from typing import Dict, Set

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.sio = socketio.AsyncServer(
            async_mode='asgi',
            cors_allowed_origins='*',
            logger=True,
            engineio_logger=True
        )
        
        # Mapeamento de usuários para suas salas
        self.user_rooms: Dict[str, Set[str]] = {}
        
        # Configurar handlers
        self.setup_handlers()
    
    def setup_handlers(self):
        @self.sio.event
        async def connect(sid, environ):
            """Cliente conectou"""
            logger.info(f"✨ Cliente conectado: {sid}")
            # Enviar mensagem de boas-vindas
            await self.sio.emit('welcome', {
                'message': 'Conectado ao Cidadão.AI'
            }, room=sid)
        
        @self.sio.event
        async def disconnect(sid):
            """Cliente desconectou"""
            logger.info(f"❌ Cliente desconectado: {sid}")
            # Remover das salas
            if sid in self.user_rooms:
                for room in self.user_rooms[sid]:
                    await self.sio.leave_room(sid, room)
                del self.user_rooms[sid]
        
        @self.sio.event
        async def join_conversation(sid, data):
            """Cliente entrou em uma conversa"""
            conversation_id = str(data.get('conversation_id'))
            if not conversation_id:
                return
            
            # Adicionar à sala da conversa
            room = f"conversation_{conversation_id}"
            await self.sio.enter_room(sid, room)
            
            # Registrar sala do usuário
            if sid not in self.user_rooms:
                self.user_rooms[sid] = set()
            self.user_rooms[sid].add(room)
            
            logger.info(f"👥 Cliente {sid} entrou na conversa {conversation_id}")
        
        @self.sio.event
        async def leave_conversation(sid, data):
            """Cliente saiu de uma conversa"""
            conversation_id = str(data.get('conversation_id'))
            if not conversation_id:
                return
            
            # Remover da sala
            room = f"conversation_{conversation_id}"
            await self.sio.leave_room(sid, room)
            
            # Atualizar registro
            if sid in self.user_rooms:
                self.user_rooms[sid].discard(room)
            
            logger.info(f"👋 Cliente {sid} saiu da conversa {conversation_id}")
    
    async def emit_new_message(self, conversation_id: int, message: dict):
        """Emitir nova mensagem para todos na conversa"""
        room = f"conversation_{conversation_id}"
        await self.sio.emit('new_message', {
            'conversation_id': conversation_id,
            'message': message
        }, room=room)
        logger.info(f"📨 Nova mensagem emitida para conversa {conversation_id}")
    
    async def emit_conversation_update(self, conversation: dict):
        """Emitir atualização de conversa para todos"""
        await self.sio.emit('conversation_update', {
            'conversation': conversation
        })
        logger.info(f"📝 Atualização de conversa emitida: {conversation.get('id')}")
    
    async def emit_typing_status(self, conversation_id: int, user: dict, is_typing: bool):
        """Emitir status de digitação"""
        room = f"conversation_{conversation_id}"
        await self.sio.emit('typing_status', {
            'conversation_id': conversation_id,
            'user': user,
            'is_typing': is_typing
        }, room=room)
        logger.info(f"⌨️ Status de digitação emitido para conversa {conversation_id}")

# Criar instância global
ws_manager = WebSocketManager()

# Criar aplicativo ASGI
app = socketio.ASGIApp(ws_manager.sio)