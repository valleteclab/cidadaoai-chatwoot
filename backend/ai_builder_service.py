"""
Serviço para construção e gerenciamento de agentes IA
"""
import os
import logging
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from .models import ConfigIA
from .chamados_service import chamados_service

logger = logging.getLogger(__name__)


class AIBuilderService:
    """Serviço para construção de agentes IA"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Any]:
        """Carregar templates pré-definidos"""
        return {
            "infraestrutura": {
                "name": "Agente de Infraestrutura",
                "system_prompt": """Você é um assistente especializado em atendimento ao cidadão para problemas de infraestrutura urbana.

SUAS RESPONSABILIDADES:
- Coletar dados do cidadão de forma amigável
- Categorizar problemas de infraestrutura
- Gerar protocolos únicos
- Fornecer informações sobre prazos

CATEGORIAS DE INFRAESTRUTURA:
- Buracos nas ruas
- Problemas de iluminação pública
- Vazamentos de água
- Danos em calçadas
- Problemas de drenagem

SEMPRE:
- Seja educado e prestativo
- Confirme informações importantes
- Explique os próximos passos
- Forneça o protocolo gerado""",
                "flow": [
                    {"step": "initial", "action": "detect_new_conversation"},
                    {"step": "greeting", "action": "greet_citizen"},
                    {"step": "data_collection", "action": "collect_citizen_data"},
                    {"step": "issue_categorization", "action": "categorize_issue"},
                    {"step": "protocol_generation", "action": "generate_protocol"},
                    {"step": "confirmation", "action": "confirm_ticket"}
                ],
                "templates": {
                    "greeting": "Olá! Sou o assistente da prefeitura para infraestrutura. Como posso te ajudar hoje?",
                    "data_collection": "Para criar seu chamado, preciso de algumas informações:\n\n1. Nome completo\n2. Telefone\n3. Endereço do problema\n4. Descrição detalhada\n\nPode me informar seu nome?",
                    "confirmation": "Perfeito! Confirme se os dados estão corretos:\n\nNome: {nome}\nTelefone: {telefone}\nEndereço: {endereco}\n\nProblema: {problema}\n\nEstá tudo certo?",
                    "protocol": "✅ Seu chamado foi criado com sucesso!\n\n📋 Protocolo: {protocolo}\n📅 Prazo: {prazo}\n🏢 Categoria: {categoria}\n\nVocê pode consultar o status a qualquer momento usando este protocolo."
                }
            },
            "saude": {
                "name": "Agente de Saúde",
                "system_prompt": """Você é um assistente especializado em atendimento ao cidadão para questões de saúde pública.

SUAS RESPONSABILIDADES:
- Coletar dados do cidadão
- Categorizar problemas de saúde
- Priorizar casos urgentes
- Fornecer orientações básicas

CATEGORIAS DE SAÚDE:
- Agendamento de consultas
- Problemas em unidades de saúde
- Emergências médicas
- Vacinação
- Programas de saúde

SEMPRE:
- Seja empático e profissional
- Priorize casos urgentes
- Forneça informações claras
- Oriente sobre procedimentos""",
                "flow": [
                    {"step": "initial", "action": "detect_new_conversation"},
                    {"step": "greeting", "action": "greet_citizen"},
                    {"step": "urgency_check", "action": "check_urgency"},
                    {"step": "data_collection", "action": "collect_citizen_data"},
                    {"step": "issue_categorization", "action": "categorize_health_issue"},
                    {"step": "protocol_generation", "action": "generate_protocol"},
                    {"step": "confirmation", "action": "confirm_ticket"}
                ],
                "templates": {
                    "greeting": "Olá! Sou o assistente da prefeitura para questões de saúde. Como posso te ajudar?",
                    "urgency_check": "Primeiro, preciso saber: este é um caso de emergência que requer atendimento imediato?",
                    "data_collection": "Para criar seu chamado, preciso de algumas informações:\n\n1. Nome completo\n2. Telefone\n3. Data de nascimento\n4. Tipo de problema\n\nPode me informar seu nome?",
                    "confirmation": "Perfeito! Confirme se os dados estão corretos:\n\nNome: {nome}\nTelefone: {telefone}\nTipo: {tipo}\n\nProblema: {problema}\n\nEstá tudo certo?",
                    "protocol": "✅ Seu chamado foi criado com sucesso!\n\n📋 Protocolo: {protocolo}\n📅 Prazo: {prazo}\n🏥 Categoria: {categoria}\n\nPara emergências, ligue para 192."
                }
            }
        }
    
    async def get_templates(self) -> Dict[str, Any]:
        """Obter todos os templates disponíveis"""
        return self.templates
    
    async def create_agent_config(self, config_data: Dict[str, Any], prefeitura_id: int = 1) -> Dict[str, Any]:
        """Criar nova configuração de agente"""
        try:
            async with chamados_service.pool.acquire() as conn:
                # Preparar dados da configuração
                agent_config = {
                    "name": config_data.get("name", "Novo Agente"),
                    "provider": config_data.get("provider", "groq"),
                    "temperature": config_data.get("temperature", 0.7),
                    "max_tokens": config_data.get("max_tokens", 1000),
                    "system_prompt": config_data.get("system_prompt", ""),
                    "flow": config_data.get("flow", []),
                    "templates": config_data.get("templates", {}),
                    "category": config_data.get("category", "geral"),
                    "sla_hours": config_data.get("sla", 24),
                    "priority": config_data.get("priority", "media"),
                    "active": config_data.get("active", True)
                }
                
                # Inserir no banco
                result = await conn.fetchrow("""
                    INSERT INTO config_ia (
                        prefeitura_id, nome, provider, config, active, created_at
                    ) VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING id, nome, provider, config, active, created_at
                """, prefeitura_id, agent_config["name"], agent_config["provider"], 
                    json.dumps(agent_config), agent_config["active"], datetime.now())
                
                return {
                    "status": "success",
                    "message": "Agente criado com sucesso",
                    "agent": {
                        "id": result["id"],
                        "nome": result["nome"],
                        "provider": result["provider"],
                        "config": result["config"],
                        "active": result["active"],
                        "created_at": result["created_at"].isoformat()
                    }
                }
                
        except Exception as e:
            logger.error(f"❌ Erro ao criar agente: {e}")
            return {
                "status": "error",
                "message": f"Erro ao criar agente: {str(e)}"
            }
    
    async def update_agent_config(self, agent_id: int, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Atualizar configuração de agente"""
        try:
            async with chamados_service.pool.acquire() as conn:
                # Preparar dados atualizados
                agent_config = {
                    "name": config_data.get("name"),
                    "provider": config_data.get("provider"),
                    "temperature": config_data.get("temperature"),
                    "max_tokens": config_data.get("max_tokens"),
                    "system_prompt": config_data.get("system_prompt"),
                    "flow": config_data.get("flow"),
                    "templates": config_data.get("templates"),
                    "category": config_data.get("category"),
                    "sla_hours": config_data.get("sla"),
                    "priority": config_data.get("priority"),
                    "active": config_data.get("active")
                }
                
                # Atualizar no banco
                result = await conn.fetchrow("""
                    UPDATE config_ia 
                    SET nome = $2, provider = $3, config = $4, updated_at = $5
                    WHERE id = $1
                    RETURNING id, nome, provider, config, active, updated_at
                """, agent_id, agent_config["name"], agent_config["provider"], 
                    json.dumps(agent_config), datetime.now())
                
                if result:
                    return {
                        "status": "success",
                        "message": "Agente atualizado com sucesso",
                        "agent": {
                            "id": result["id"],
                            "nome": result["nome"],
                            "provider": result["provider"],
                            "config": result["config"],
                            "active": result["active"],
                            "updated_at": result["updated_at"].isoformat()
                        }
                    }
                else:
                    return {
                        "status": "error",
                        "message": "Agente não encontrado"
                    }
                
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar agente: {e}")
            return {
                "status": "error",
                "message": f"Erro ao atualizar agente: {str(e)}"
            }
    
    async def list_agent_configs(self, prefeitura_id: int = 1) -> Dict[str, Any]:
        """Listar todas as configurações de agentes"""
        try:
            async with chamados_service.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT id, nome, provider, config, active, created_at, updated_at
                    FROM config_ia
                    WHERE prefeitura_id = $1
                    ORDER BY created_at DESC
                """, prefeitura_id)
                
                agents = []
                for row in results:
                    config_data = row["config"] if isinstance(row["config"], dict) else json.loads(row["config"])
                    agents.append({
                        "id": row["id"],
                        "nome": row["nome"],
                        "provider": row["provider"],
                        "config": config_data,
                        "active": row["active"],
                        "created_at": row["created_at"].isoformat(),
                        "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None
                    })
                
                return {
                    "status": "success",
                    "agents": agents,
                    "total": len(agents)
                }
                
        except Exception as e:
            logger.error(f"❌ Erro ao listar agentes: {e}")
            return {
                "status": "error",
                "message": f"Erro ao listar agentes: {str(e)}"
            }
    
    async def test_agent_config(self, config_data: Dict[str, Any], test_message: str) -> Dict[str, Any]:
        """Testar configuração de agente"""
        try:
            from .ai_providers import AIProviderFactory
            
            # Criar provedor temporário
            provider = AIProviderFactory.create_provider(
                config_data.get("provider", "groq")
            )
            
            if not provider:
                return {
                    "status": "error",
                    "message": "Provedor não disponível"
                }
            
            # Preparar mensagens
            messages = [
                {"role": "system", "content": config_data.get("system_prompt", "")},
                {"role": "user", "content": test_message}
            ]
            
            # Gerar resposta
            start_time = datetime.now()
            response = await provider.generate_response(
                messages,
                temperature=config_data.get("temperature", 0.7),
                max_tokens=config_data.get("max_tokens", 1000)
            )
            end_time = datetime.now()
            
            response_time = (end_time - start_time).total_seconds()
            
            return {
                "status": "success",
                "response": response,
                "metrics": {
                    "response_time": response_time,
                    "tokens_used": len(response.split()) if response else 0,
                    "estimated_cost": self._calculate_cost(config_data.get("provider"), len(response.split()) if response else 0)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao testar agente: {e}")
            return {
                "status": "error",
                "message": f"Erro ao testar agente: {str(e)}"
            }
    
    def _calculate_cost(self, provider: str, tokens: int) -> float:
        """Calcular custo estimado"""
        costs = {
            "groq": 0.00059,  # por 1M tokens
            "openai": 0.03,   # por 1K tokens
            "anthropic": 0.015 # por 1K tokens
        }
        
        cost_per_token = costs.get(provider, 0.001) / 1000
        return round(tokens * cost_per_token, 4)


# Instância global do serviço
ai_builder_service = AIBuilderService()
