"""
Provedores de IA - Interface abstrata para múltiplos provedores
"""
import os
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class AIProvider(ABC):
    """Interface abstrata para provedores de IA"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None
        self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self):
        """Inicializar cliente do provedor"""
        pass
    
    @abstractmethod
    async def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> Optional[str]:
        """Gerar resposta usando o provedor"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Verificar se o provedor está disponível"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Nome do provedor"""
        pass

class GroqProvider(AIProvider):
    """Provedor Groq"""
    
    def _initialize_client(self):
        try:
            from groq import Groq
            self.client = Groq(api_key=self.api_key)
            logger.info("🚀 Cliente Groq inicializado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Groq: {e}")
            self.client = None
    
    async def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> Optional[str]:
        if not self.client:
            return None
        
        try:
            response = self.client.chat.completions.create(
                model=kwargs.get("model", "llama-3.1-8b-instant"),  # Modelo atual do Groq
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 300),
                temperature=kwargs.get("temperature", 0.7),
                top_p=kwargs.get("top_p", 0.9)
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"❌ Erro ao gerar resposta com Groq: {e}")
            return None
    
    def is_available(self) -> bool:
        return self.client is not None
    
    def get_provider_name(self) -> str:
        return "Groq"

class OpenAIProvider(AIProvider):
    """Provedor OpenAI"""
    
    def _initialize_client(self):
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            logger.info("🤖 Cliente OpenAI inicializado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar OpenAI: {e}")
            self.client = None
    
    async def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> Optional[str]:
        if not self.client:
            return None
        
        try:
            response = self.client.chat.completions.create(
                model=kwargs.get("model", "gpt-3.5-turbo"),
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 300),
                temperature=kwargs.get("temperature", 0.7),
                top_p=kwargs.get("top_p", 0.9),
                frequency_penalty=kwargs.get("frequency_penalty", 0.1),
                presence_penalty=kwargs.get("presence_penalty", 0.1)
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"❌ Erro ao gerar resposta com OpenAI: {e}")
            return None
    
    def is_available(self) -> bool:
        return self.client is not None
    
    def get_provider_name(self) -> str:
        return "OpenAI"

class AnthropicProvider(AIProvider):
    """Provedor Anthropic (Claude) - Para uso futuro"""
    
    def _initialize_client(self):
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
            logger.info("🧠 Cliente Anthropic inicializado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Anthropic: {e}")
            self.client = None
    
    async def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> Optional[str]:
        if not self.client:
            return None
        
        try:
            # Converter formato de mensagens para Anthropic
            system_message = None
            user_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    user_messages.append(msg)
            
            response = self.client.messages.create(
                model=kwargs.get("model", "claude-3-sonnet-20240229"),
                max_tokens=kwargs.get("max_tokens", 300),
                system=system_message,
                messages=user_messages
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"❌ Erro ao gerar resposta com Anthropic: {e}")
            return None
    
    def is_available(self) -> bool:
        return self.client is not None
    
    def get_provider_name(self) -> str:
        return "Anthropic"

class AIProviderFactory:
    """Factory para criar provedores de IA"""
    
    @staticmethod
    def create_provider(provider_name: str, api_key: str) -> Optional[AIProvider]:
        """Criar provedor baseado no nome"""
        providers = {
            "groq": GroqProvider,
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider
        }
        
        provider_class = providers.get(provider_name.lower())
        if not provider_class:
            logger.error(f"❌ Provedor '{provider_name}' não suportado")
            return None
        
        try:
            return provider_class(api_key)
        except Exception as e:
            logger.error(f"❌ Erro ao criar provedor {provider_name}: {e}")
            return None
    
    @staticmethod
    def get_available_providers() -> List[str]:
        """Listar provedores disponíveis"""
        return ["groq", "openai", "anthropic"]
