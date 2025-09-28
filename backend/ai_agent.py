"""
Agente OpenAI para atendimento automático ao cidadão
"""
import os
import logging
from typing import Optional, Dict, Any
from openai import OpenAI
from datetime import datetime

logger = logging.getLogger(__name__)

class CidadaoAIAgent:
    """Agente de IA especializado em atendimento ao cidadão"""
    
    def __init__(self):
        self.client = None
        self.system_prompt = self._get_system_prompt()
        self.conversation_memory = {}  # Para manter contexto das conversas
        
        # Inicializar cliente OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                self.client = OpenAI(api_key=api_key)
                logger.info("✅ Cliente OpenAI inicializado com sucesso")
            except Exception as e:
                logger.error(f"❌ Erro ao inicializar OpenAI: {e}")
                self.client = None
        else:
            logger.warning("⚠️ OPENAI_API_KEY não configurada - Agente desabilitado")
    
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
        if not self.client:
            logger.warning("Cliente OpenAI não disponível")
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
            
            # Preparar mensagens para OpenAI
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Adicionar histórico (últimas 5 mensagens para manter contexto)
            for msg in conversation_history[-5:]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            logger.info(f"Enviando mensagem para OpenAI: {message[:100]}...")
            
            # Chamar OpenAI
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=300,
                temperature=0.7,
                top_p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )
            
            ai_response = response.choices[0].message.content.strip()
            
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
            logger.error(f"❌ Erro ao processar mensagem com OpenAI: {e}")
            return self._get_fallback_response()
    
    def _get_fallback_response(self) -> str:
        """Resposta de fallback quando OpenAI falha"""
        return "Olá! Recebi sua mensagem. Nossa equipe técnica irá respondê-lo em breve. Obrigado pelo contato! 😊"
    
    def is_available(self) -> bool:
        """Verificar se o agente está disponível"""
        return self.client is not None
    
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
