"""
Agente especializado em categorização de problemas
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from .base_agent import BaseAgent, AgentMessage
from ..ai_providers import AIProviderFactory

logger = logging.getLogger(__name__)

class CategorizationAgent(BaseAgent):
    """Agente especializado em categorizar problemas de cidadãos"""
    
    def __init__(self):
        super().__init__(
            agent_id="categorization_agent",
            agent_name="Agente de Categorização",
            agent_type="categorization"
        )
        
        # Configurar provedor de IA
        self.ai_provider = self._setup_ai_provider()
        
        # Categorias pré-definidas
        self.categories = {
            "infraestrutura": {
                "keywords": ["buraco", "rua", "iluminação", "luz", "vazamento", "água", "esgoto", "calçada", "pavimento"],
                "priority": "alta",
                "sla_hours": 24,
                "time_nome": "Secretaria de Infraestrutura"
            },
            "saude": {
                "keywords": ["posto", "saúde", "médico", "medicamento", "vacina", "hospital", "emergência", "atendimento"],
                "priority": "critica", 
                "sla_hours": 4,
                "time_nome": "Secretaria de Saúde"
            },
            "educacao": {
                "keywords": ["escola", "educação", "matrícula", "merenda", "transporte", "professor", "aluno", "ensino"],
                "priority": "media",
                "sla_hours": 48,
                "time_nome": "Secretaria de Educação"
            },
            "assistencia_social": {
                "keywords": ["bolsa", "benefício", "cadastro", "assistência", "social", "auxílio", "renda", "família"],
                "priority": "media",
                "sla_hours": 72,
                "time_nome": "Secretaria de Assistência Social"
            },
            "obras": {
                "keywords": ["obra", "construção", "reforma", "pavimentação", "asfalto", "construir", "reformar", "melhorar"],
                "priority": "alta",
                "sla_hours": 168,
                "time_nome": "Secretaria de Obras"
            }
        }
        
        logger.info("🏷️ Agente de Categorização inicializado")
    
    def _setup_ai_provider(self):
        """Configurar provedor de IA"""
        import os
        
        # Tentar Groq primeiro (mais rápido)
        if os.getenv("GROQ_API_KEY"):
            provider = AIProviderFactory.create_provider("groq", os.getenv("GROQ_API_KEY"))
            if provider and provider.is_available():
                return provider
        
        # Fallback para OpenAI
        if os.getenv("OPENAI_API_KEY"):
            provider = AIProviderFactory.create_provider("openai", os.getenv("OPENAI_API_KEY"))
            if provider and provider.is_available():
                return provider
        
        logger.warning("⚠️ Nenhum provedor de IA disponível para categorização")
        return None
    
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Processar mensagem de categorização"""
        start_time = datetime.now()
        
        try:
            if message.event == "categorize_issue":
                result = await self._categorize_issue(message.data)
                
                # Atualizar métricas
                response_time = (datetime.now() - start_time).total_seconds()
                self.update_metrics(response_time, result is not None)
                
                if result:
                    # Enviar resultado para agente de chamados
                    response = AgentMessage(
                        event="issue_categorized",
                        from_agent=self.agent_id,
                        to_agent="ticket_agent",
                        conversation_id=message.conversation_id,
                        data={
                            **message.data,
                            "categorization": result
                        },
                        timestamp=datetime.now(),
                        priority=1
                    )
                    
                    logger.info(f"✅ Problema categorizado: {result['category']} (confiança: {result['confidence']:.2f})")
                    return response
                else:
                    logger.warning("❌ Falha na categorização do problema")
                    return None
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro no processamento de categorização: {e}")
            response_time = (datetime.now() - start_time).total_seconds()
            self.update_metrics(response_time, False)
            return None
    
    async def handle_event(self, event: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Manipular eventos específicos"""
        if event == "categorize":
            return await self._categorize_issue(data)
        elif event == "get_categories":
            return {"categories": list(self.categories.keys())}
        elif event == "get_category_info":
            category = data.get("category")
            return self.categories.get(category)
        
        return None
    
    async def _categorize_issue(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Categorizar problema usando IA e regras"""
        try:
            description = data.get("description", "").lower()
            
            if not description:
                return None
            
            # Primeiro, tentar categorização por palavras-chave
            keyword_result = self._categorize_by_keywords(description)
            
            # Se IA disponível, usar para melhorar a categorização
            if self.ai_provider:
                ai_result = await self._categorize_with_ai(description)
                
                # Combinar resultados
                if ai_result and ai_result["confidence"] > 0.7:
                    # IA tem alta confiança, usar resultado da IA
                    result = ai_result
                elif keyword_result["confidence"] > 0.6:
                    # Palavras-chave têm boa confiança, usar resultado das keywords
                    result = keyword_result
                else:
                    # Ambos têm baixa confiança, usar IA se disponível
                    result = ai_result if ai_result else keyword_result
            else:
                # Sem IA, usar apenas palavras-chave
                result = keyword_result
            
            if result and result["category"]:
                # Adicionar informações da categoria
                category_info = self.categories.get(result["category"], {})
                result.update({
                    "priority": category_info.get("priority", "media"),
                    "sla_hours": category_info.get("sla_hours", 72),
                    "time_nome": category_info.get("time_nome", "Secretaria Geral")
                })
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro na categorização: {e}")
            return None
    
    def _categorize_by_keywords(self, description: str) -> Dict[str, Any]:
        """Categorizar usando palavras-chave"""
        description_lower = description.lower()
        
        best_category = None
        best_score = 0
        
        for category, info in self.categories.items():
            score = 0
            keywords = info["keywords"]
            
            # Contar palavras-chave encontradas
            for keyword in keywords:
                if keyword in description_lower:
                    score += 1
            
            # Normalizar score (0-1)
            normalized_score = score / len(keywords)
            
            if normalized_score > best_score:
                best_score = normalized_score
                best_category = category
        
        return {
            "category": best_category,
            "confidence": best_score,
            "method": "keywords"
        }
    
    async def _categorize_with_ai(self, description: str) -> Optional[Dict[str, Any]]:
        """Categorizar usando IA"""
        try:
            categories_list = list(self.categories.keys())
            
            prompt = f"""Analise a seguinte descrição de problema e categorize em uma das categorias disponíveis:

Descrição: "{description}"

Categorias disponíveis:
- infraestrutura: problemas de ruas, iluminação, água, esgoto, calçadas
- saude: problemas de postos de saúde, médicos, medicamentos, vacinação
- educacao: problemas de escolas, matrículas, merenda, transporte escolar
- assistencia_social: problemas de benefícios, cadastros, auxílios
- obras: problemas de construções, reformas, pavimentação

Responda APENAS com o nome da categoria (ex: "infraestrutura") e sua confiança de 0 a 1 (ex: "0.85").

Formato: categoria|confiança"""

            messages = [
                {"role": "system", "content": "Você é um especialista em categorização de problemas públicos."},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.ai_provider.generate_response(
                messages=messages,
                max_tokens=50,
                temperature=0.3
            )
            
            if response:
                # Parse da resposta
                parts = response.strip().split('|')
                if len(parts) == 2:
                    category = parts[0].strip().lower()
                    confidence = float(parts[1].strip())
                    
                    if category in self.categories:
                        return {
                            "category": category,
                            "confidence": confidence,
                            "method": "ai"
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro na categorização por IA: {e}")
            return None
