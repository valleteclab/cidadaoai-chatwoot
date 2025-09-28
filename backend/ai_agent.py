"""
Agente de IA para atendimento automático ao cidadão - Suporte múltiplos provedores
"""
import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from .ai_providers import AIProviderFactory

logger = logging.getLogger(__name__)

class CidadaoAIAgent:
    """Agente de IA especializado em atendimento ao cidadão"""
    
    def __init__(self):
        self.provider = None
        self.system_prompt = self._get_system_prompt()
        self.conversation_memory = {}  # Para manter contexto das conversas
        
        # Configurar provedor de IA
        self._setup_ai_provider()
    
    def _setup_ai_provider(self):
        """Configurar provedor de IA baseado nas variáveis de ambiente"""
        # Prioridade: Groq > OpenAI > Anthropic
        provider_configs = [
            ("groq", os.getenv("GROQ_API_KEY")),
            ("openai", os.getenv("OPENAI_API_KEY")),
            ("anthropic", os.getenv("ANTHROPIC_API_KEY"))
        ]
        
        for provider_name, api_key in provider_configs:
            if api_key:
                self.provider = AIProviderFactory.create_provider(provider_name, api_key)
                if self.provider and self.provider.is_available():
                    logger.info(f"✅ Provedor {provider_name} configurado e disponível")
                    return
        
        logger.warning("⚠️ Nenhum provedor de IA configurado - Agente desabilitado")
        self.provider = None
    
    def _get_system_prompt(self) -> str:
        """Prompt do sistema para o agente"""
        return """
        Você é um assistente virtual especializado em atendimento ao cidadão para prefeituras brasileiras.
        
        Suas principais responsabilidades:
        - Fornecer informações sobre serviços municipais
        - Orientar sobre documentos e procedimentos
        - Explicar questões tributárias (IPTU, ISS, etc.)
        - Informar sobre saúde, educação e outros serviços públicos
        - Ser prestativo, educado e profissional
        
        Diretrizes importantes:
        - Use linguagem clara e acessível
        - Seja sempre cortês e respeitoso
        - Se não souber algo específico, oriente o cidadão a entrar em contato com o órgão responsável
        - Mantenha foco em informações gerais e orientações básicas
        - Se a questão for complexa, sugira que o cidadão fale com um técnico humano
        
        Formato das respostas:
        - Seja direto e objetivo
        - Use emojis moderadamente para tornar a comunicação mais amigável
        - Sempre termine oferecendo ajuda adicional
        
        Exemplo de resposta:
        "Olá! Para informações sobre IPTU, você pode consultar o portal da prefeitura ou ligar para a Secretaria da Fazenda. Posso ajudá-lo com mais alguma coisa?"
        """
    
    async def process_message(self, message: str, conversation_id: int, contact_info: Dict[str, Any] = None) -> Optional[str]:
        """
        Processar mensagem e gerar resposta automática
        
        Args:
            message: Mensagem recebida do cidadão
            conversation_id: ID da conversa
            contact_info: Informações do contato (opcional)
        
        Returns:
            Resposta gerada pelo agente ou None se erro
        """
        logger.info(f"🤖 INÍCIO PROCESSAMENTO IA - Conversa {conversation_id}")
        logger.info(f"📝 Mensagem recebida: {message[:100]}...")
        logger.info(f"🔧 Provedor atual: {self.get_provider_name()}")
        
        if not self.provider:
            logger.error("🚨 ERRO: Provedor de IA não disponível")
            return None
        
        if not self.provider.is_available():
            logger.error(f"🚨 ERRO: Provedor {self.get_provider_name()} não está disponível")
            return None
        
        try:
            # Preparar contexto da conversa
            conversation_key = f"conv_{conversation_id}"
            
            # Obter histórico da conversa (se existir)
            conversation_history = self.conversation_memory.get(conversation_key, [])
            
            # Adicionar mensagem atual ao histórico
            conversation_history.append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat()
            })
            
            # Preparar mensagens para o provedor
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Adicionar histórico (últimas 5 mensagens para manter contexto)
            for msg in conversation_history[-5:]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            logger.info(f"🚀 ENVIANDO PARA {self.provider.get_provider_name()}: {message[:100]}...")
            logger.info(f"📊 Mensagens preparadas: {len(messages)}")
            
            # Chamar provedor de IA
            ai_response = await self.provider.generate_response(
                messages=messages,
                max_tokens=300,
                temperature=0.7,
                top_p=0.9
            )
            
            logger.info(f"📥 RESPOSTA RECEBIDA: {ai_response[:200] if ai_response else 'NENHUMA'}...")
            
            if not ai_response:
                logger.error("🚨 ERRO: Provedor não retornou resposta")
                return self._get_fallback_response()
            
            # Adicionar resposta ao histórico
            conversation_history.append({
                "role": "assistant",
                "content": ai_response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Manter apenas últimas 10 mensagens para não sobrecarregar
            self.conversation_memory[conversation_key] = conversation_history[-10:]
            
            logger.info(f"✅ Resposta gerada: {ai_response[:100]}...")
            
            return ai_response
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar mensagem com {self.provider.get_provider_name() if self.provider else 'IA'}: {e}")
            return self._get_fallback_response()
    
    def _get_fallback_response(self) -> str:
        """Resposta de fallback quando IA falha"""
        logger.error("🚨 FALLBACK ATIVADO - IA REAL NÃO FUNCIONOU!")
        return "🚨 ERRO: IA não conseguiu processar. Provedor ativo: " + self.get_provider_name()
    
    def is_available(self) -> bool:
        """Verificar se o agente está disponível"""
        return self.provider is not None and self.provider.is_available()
    
    def get_provider_name(self) -> str:
        """Obter nome do provedor atual"""
        return self.provider.get_provider_name() if self.provider else "Nenhum"
    
    def get_conversation_context(self, conversation_id: int) -> list:
        """Obter contexto de uma conversa específica"""
        conversation_key = f"conv_{conversation_id}"
        return self.conversation_memory.get(conversation_key, [])
    
    def clear_conversation_context(self, conversation_id: int):
        """Limpar contexto de uma conversa específica"""
        conversation_key = f"conv_{conversation_id}"
        if conversation_key in self.conversation_memory:
            del self.conversation_memory[conversation_key]
            logger.info(f"Contexto da conversa {conversation_id} limpo")

# Instância global do agente
ai_agent = CidadaoAIAgent()
