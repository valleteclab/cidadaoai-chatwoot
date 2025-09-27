"""
Módulo para transcrição de áudio usando OpenAI Whisper API
"""
import os
import logging
from openai import OpenAI
from typing import Optional

logger = logging.getLogger(__name__)

class AudioTranscriber:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AudioTranscriber, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Evitar inicialização múltipla
        if AudioTranscriber._initialized:
            return
        
        AudioTranscriber._initialized = True
        self.client = None  # Será inicializado sob demanda

    def initialize(self):
        """Inicializar cliente OpenAI (chamado após carregar .env)"""
        if self.client is not None:
            return

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("❌ OpenAI API Key não encontrada no .env!")
            raise ValueError("OPENAI_API_KEY não configurada")
        
        logger.info(f"🔑 OpenAI API Key configurada: {api_key[:10]}...")
        self.client = OpenAI(api_key=api_key)
        logger.info("✅ Cliente OpenAI inicializado")

    async def transcribe(self, audio_path: str) -> Optional[str]:
        """Transcrever áudio usando OpenAI Whisper API"""
        if self.client is None:
            self.initialize()

        try:
            logger.info(f"🎯 Transcrevendo áudio: {audio_path}")
            
            with open(audio_path, "rb") as audio_file:
                # Transcrever usando Whisper
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="pt"
                )
                
                # Extrair texto
                text = response.text
                logger.info(f"✅ Transcrição concluída: {text[:100]}...")
                return text
                
        except Exception as e:
            logger.error(f"❌ Erro na transcrição: {str(e)}")
            return None

# Criar instância global (sem inicializar ainda)
transcriber = AudioTranscriber()
