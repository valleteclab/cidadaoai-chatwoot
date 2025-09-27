# AI service for processing messages and generating responses
import openai
import os
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class IAService:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    async def generate_response(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate AI response for a given message
        
        Args:
            message: User message to respond to
            context: Additional context for the conversation
            
        Returns:
            Generated response string
        """
        try:
            # Build the conversation context
            messages = [
                {
                    "role": "system",
                    "content": "Você é um assistente virtual especializado em atendimento ao cidadão. "
                              "Seja prestativo, educado e forneça informações precisas."
                }
            ]
            
            # Add context if provided
            if context:
                context_str = f"Contexto da conversa: {context}"
                messages.append({"role": "system", "content": context_str})
            
            # Add user message
            messages.append({"role": "user", "content": message})
            
            # Generate response
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return "Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente."
    
    async def analyze_intent(self, message: str) -> Dict[str, Any]:
        """
        Analyze user message intent
        
        Args:
            message: User message to analyze
            
        Returns:
            Dictionary with intent analysis results
        """
        try:
            prompt = f"""
            Analise a seguinte mensagem e identifique a intenção do usuário:
            
            Mensagem: "{message}"
            
            Retorne um JSON com:
            - intent: categoria da intenção
            - confidence: nível de confiança (0-1)
            - entities: entidades identificadas
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3
            )
            
            # TODO: Parse JSON response properly
            return {"intent": "general", "confidence": 0.8, "entities": []}
            
        except Exception as e:
            logger.error(f"Error analyzing intent: {str(e)}")
            return {"intent": "unknown", "confidence": 0.0, "entities": []}

# Global IA service instance
ia_service = IAService()
