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
                "description": "Atende problemas de infraestrutura urbana como buracos, iluminação e vazamentos",
                "category": "infraestrutura",
                "sla": 24,
                "priority": "alta",
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
                "description": "Atende questões de saúde pública, agendamentos e emergências",
                "category": "saude",
                "sla": 4,
                "priority": "critica",
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
            },
            "educacao": {
                "name": "Agente de Educação",
                "description": "Atende questões relacionadas à educação municipal",
                "category": "educacao",
                "sla": 48,
                "priority": "media",
                "system_prompt": """Você é um assistente especializado em atendimento ao cidadão para questões de educação municipal.

SUAS RESPONSABILIDADES:
- Orientar sobre matrículas escolares
- Informar sobre transporte escolar
- Resolver questões de merenda
- Fornecer informações sobre programas educacionais

CATEGORIAS DE EDUCAÇÃO:
- Matrículas escolares
- Transporte escolar
- Merenda escolar
- Material didático
- Programas educacionais

SEMPRE:
- Seja paciente e educativo
- Forneça informações claras sobre prazos
- Oriente sobre documentos necessários
- Explique procedimentos passo a passo""",
                "flow": [
                    {"step": "initial", "action": "detect_new_conversation"},
                    {"step": "greeting", "action": "greet_citizen"},
                    {"step": "data_collection", "action": "collect_citizen_data"},
                    {"step": "issue_categorization", "action": "categorize_education_issue"},
                    {"step": "protocol_generation", "action": "generate_protocol"},
                    {"step": "confirmation", "action": "confirm_ticket"}
                ],
                "templates": {
                    "greeting": "Olá! Sou o assistente da prefeitura para questões de educação. Como posso te ajudar?",
                    "data_collection": "Para te ajudar melhor, preciso de algumas informações:\n\n1. Nome completo\n2. Telefone\n3. Nome do aluno (se aplicável)\n4. Tipo de questão\n\nPode me informar seu nome?",
                    "confirmation": "Perfeito! Confirme se os dados estão corretos:\n\nNome: {nome}\nTelefone: {telefone}\nTipo: {tipo}\n\nQuestão: {questao}\n\nEstá tudo certo?",
                    "protocol": "✅ Seu chamado foi criado com sucesso!\n\n📋 Protocolo: {protocolo}\n📅 Prazo: {prazo}\n🎓 Categoria: {categoria}\n\nVocê pode consultar o status a qualquer momento."
                }
            },
            "assistencia_social": {
                "name": "Agente de Assistência Social",
                "description": "Atende questões de assistência social e benefícios",
                "category": "assistencia_social",
                "sla": 72,
                "priority": "media",
                "system_prompt": """Você é um assistente especializado em atendimento ao cidadão para questões de assistência social.

SUAS RESPONSABILIDADES:
- Orientar sobre benefícios sociais
- Informar sobre cadastros
- Esclarecer dúvidas sobre programas
- Fornecer informações sobre documentação

CATEGORIAS DE ASSISTÊNCIA SOCIAL:
- Cadastro Único
- Bolsa Família
- Benefícios de Prestação Continuada
- Programas sociais municipais
- Auxílio emergencial

SEMPRE:
- Seja empático e respeitoso
- Proteja a privacidade das informações
- Forneça orientações claras
- Explique prazos e procedimentos""",
                "flow": [
                    {"step": "initial", "action": "detect_new_conversation"},
                    {"step": "greeting", "action": "greet_citizen"},
                    {"step": "data_collection", "action": "collect_citizen_data"},
                    {"step": "issue_categorization", "action": "categorize_social_issue"},
                    {"step": "protocol_generation", "action": "generate_protocol"},
                    {"step": "confirmation", "action": "confirm_ticket"}
                ],
                "templates": {
                    "greeting": "Olá! Sou o assistente da prefeitura para assistência social. Como posso te ajudar?",
                    "data_collection": "Para te orientar melhor, preciso de algumas informações:\n\n1. Nome completo\n2. Telefone\n3. CPF\n4. Tipo de questão\n\nPode me informar seu nome?",
                    "confirmation": "Perfeito! Confirme se os dados estão corretos:\n\nNome: {nome}\nTelefone: {telefone}\nTipo: {tipo}\n\nQuestão: {questao}\n\nEstá tudo certo?",
                    "protocol": "✅ Seu chamado foi criado com sucesso!\n\n📋 Protocolo: {protocolo}\n📅 Prazo: {prazo}\n🤝 Categoria: {categoria}\n\nVocê pode consultar o status a qualquer momento."
                }
            },
            "vendas": {
                "name": "Agente de Vendas",
                "description": "Agente especializado em vendas e atendimento comercial",
                "category": "vendas",
                "sla": 2,
                "priority": "alta",
                "system_prompt": """Você é um assistente comercial especializado em vendas e atendimento ao cliente.

SUAS RESPONSABILIDADES:
- Qualificar leads e oportunidades
- Apresentar produtos e serviços
- Fechar negócios
- Manter relacionamento com clientes

TÉCNICAS DE VENDAS:
- Identificar necessidades do cliente
- Apresentar soluções adequadas
- Superar objeções
- Criar urgência quando apropriado

SEMPRE:
- Seja profissional e consultivo
- Ouça ativamente o cliente
- Personalize a abordagem
- Foque na solução, não no produto""",
                "flow": [
                    {"step": "initial", "action": "detect_new_conversation"},
                    {"step": "greeting", "action": "greet_prospect"},
                    {"step": "qualification", "action": "qualify_lead"},
                    {"step": "presentation", "action": "present_solution"},
                    {"step": "objection_handling", "action": "handle_objections"},
                    {"step": "closing", "action": "close_deal"}
                ],
                "templates": {
                    "greeting": "Olá! Como posso te ajudar hoje?",
                    "qualification": "Para te apresentar a melhor solução, preciso entender melhor suas necessidades. Pode me contar sobre seu projeto?",
                    "presentation": "Baseado no que você me contou, tenho uma solução perfeita para você...",
                    "closing": "Que tal agendarmos uma conversa para discutir os detalhes?"
                }
            }
        }
    
    async def get_templates(self) -> Dict[str, Any]:
        """Obter todos os templates disponíveis"""
        return self.templates
    
    async def get_active_agent_for_message(self, message: str) -> Optional[Dict[str, Any]]:
        """Obter agente ativo apropriado para a mensagem"""
        try:
            async with chamados_service.pool.acquire() as conn:
                # Buscar agentes ativos ordenados por prioridade
                agents = await conn.fetch("""
                    SELECT id, nome, provider, config, category, sla_hours, priority, active
                    FROM config_ia 
                    WHERE active = true 
                    ORDER BY 
                        CASE priority 
                            WHEN 'critica' THEN 1 
                            WHEN 'alta' THEN 2 
                            WHEN 'media' THEN 3 
                            WHEN 'baixa' THEN 4 
                        END,
                        sla_hours ASC
                """)
                
                if not agents:
                    return None
                
                # Para cada agente, verificar se a mensagem se encaixa na categoria
                for agent in agents:
                    config = agent['config'] if isinstance(agent['config'], dict) else {}
                    category = agent['category']
                    
                    # Verificar keywords da categoria
                    if self._message_matches_category(message, category):
                        return {
                            'id': agent['id'],
                            'name': agent['nome'],
                            'provider': agent['provider'],
                            'category': category,
                            'sla_hours': agent['sla_hours'],
                            'priority': agent['priority'],
                            'config': config
                        }
                
                # Se nenhum agente específico foi encontrado, retornar o primeiro ativo
                first_agent = agents[0]
                config = first_agent['config'] if isinstance(first_agent['config'], dict) else {}
                
                return {
                    'id': first_agent['id'],
                    'name': first_agent['nome'],
                    'provider': first_agent['provider'],
                    'category': first_agent['category'],
                    'sla_hours': first_agent['sla_hours'],
                    'priority': first_agent['priority'],
                    'config': config
                }
                
        except Exception as e:
            logger.error(f"Erro ao buscar agente ativo: {e}")
            return None
    
    def _message_matches_category(self, message: str, category: str) -> bool:
        """Verificar se mensagem se encaixa na categoria do agente"""
        message_lower = message.lower()
        
        category_keywords = {
            'infraestrutura': ['buraco', 'rua', 'asfalto', 'calçada', 'iluminação', 'esgoto', 'poste', 'pavimentação', 'vazamento'],
            'saude': ['posto', 'saúde', 'médico', 'remédio', 'hospital', 'clínica', 'atendimento', 'consulta', 'vacina'],
            'educacao': ['escola', 'educação', 'professor', 'merenda', 'transporte', 'ensino', 'matrícula', 'aluno'],
            'assistencia_social': ['bolsa', 'assistência', 'social', 'cadastro', 'benefício', 'auxílio', 'família'],
            'vendas': ['venda', 'comprar', 'produto', 'serviço', 'comercial', 'preço', 'orçamento']
        }
        
        keywords = category_keywords.get(category, [])
        return any(keyword in message_lower for keyword in keywords)
    
    async def process_message_with_agent(self, agent_config: Dict[str, Any], message: str, 
                                       conversation_id: int, contact_info: Dict[str, Any] = None) -> Optional[str]:
        """Processar mensagem usando agente específico do AI Builder"""
        try:
            from .ai_providers import get_provider
            
            # Obter provedor de IA
            provider_name = agent_config.get('provider', 'groq')
            provider = get_provider(provider_name)
            
            if not provider or not provider.is_available():
                logger.warning(f"Provedor {provider_name} não disponível")
                return None
            
            # Preparar prompt do sistema
            system_prompt = agent_config.get('config', {}).get('system_prompt', 
                                                             self.templates.get(agent_config.get('category', 'infraestrutura'), {}).get('system_prompt', ''))
            
            if not system_prompt:
                logger.warning("Nenhum prompt do sistema encontrado")
                return None
            
            # Preparar mensagens
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
            
            # Gerar resposta
            ai_response = await provider.generate_response(
                messages=messages,
                max_tokens=agent_config.get('config', {}).get('max_tokens', 1000),
                temperature=agent_config.get('config', {}).get('temperature', 0.7)
            )
            
            if ai_response:
                # Log da interação
                await self._log_agent_interaction(
                    agent_id=agent_config['id'],
                    user_message=message,
                    ai_response=ai_response,
                    conversation_id=conversation_id
                )
                
                return ai_response
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem com agente: {e}")
            return None
    
    async def _log_agent_interaction(self, agent_id: int, user_message: str, ai_response: str, 
                                   conversation_id: int, response_time: float = 0.0, 
                                   tokens_used: int = 0, cost: float = 0.0):
        """Registrar interação do agente para analytics"""
        try:
            async with chamados_service.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO agent_interactions 
                    (agent_id, user_message, ai_response, response_time, tokens_used, cost, success, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """, agent_id, user_message, ai_response, response_time, tokens_used, cost, True, 
                    json.dumps({"conversation_id": conversation_id}))
        except Exception as e:
            logger.error(f"Erro ao registrar interação do agente: {e}")
    
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
                    try:
                        config_data = row["config"] if isinstance(row["config"], dict) else json.loads(row["config"] or '{}')
                        
                        # Extrair dados do config
                        category = config_data.get('category', 'geral')
                        sla_hours = config_data.get('sla_hours', config_data.get('sla', 24))
                        priority = config_data.get('priority', 'media')
                        system_prompt = config_data.get('system_prompt', '')
                        
                        # Buscar última atividade do agente
                        last_activity = await conn.fetchval("""
                            SELECT MAX(created_at) 
                            FROM agent_interactions 
                            WHERE agent_id = $1
                        """, row["id"])
                        
                        agents.append({
                            "id": row["id"],
                            "name": row["nome"],  # Mudança: usar 'name' em vez de 'nome'
                            "provider": row["provider"],
                            "category": category,
                            "sla_hours": sla_hours,
                            "priority": priority,
                            "config": config_data,
                            "active": row["active"],
                            "created_at": row["created_at"].isoformat(),
                            "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
                            "last_activity": last_activity.isoformat() if last_activity else None,
                            "system_prompt": system_prompt[:100] + "..." if len(system_prompt) > 100 else system_prompt
                        })
                    except Exception as e:
                        logger.error(f"Erro ao processar agente {row['id']}: {e}")
                        continue
                
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
            
            # Criar provedor temporário com API key
            provider_name = config_data.get("provider", "groq")
            api_key = os.getenv(f"{provider_name.upper()}_API_KEY")
            
            if not api_key:
                return {
                    "status": "error",
                    "message": f"API key não configurada para {provider_name}"
                }
            
            provider = AIProviderFactory.create_provider(provider_name, api_key)
            
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
    
    async def get_agent_config(self, agent_id: int) -> Dict[str, Any]:
        """Obter configuração de agente específico"""
        try:
            async with chamados_service.pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT id, nome, provider, config, active, created_at, updated_at
                    FROM config_ia
                    WHERE id = $1
                """, agent_id)
                
                if result:
                    config_data = result["config"] if isinstance(result["config"], dict) else json.loads(result["config"])
                    return {
                        "status": "success",
                        "agent": {
                            "id": result["id"],
                            "nome": result["nome"],
                            "provider": result["provider"],
                            "config": config_data,
                            "active": result["active"],
                            "created_at": result["created_at"].isoformat(),
                            "updated_at": result["updated_at"].isoformat() if result["updated_at"] else None
                        }
                    }
                else:
                    return {
                        "status": "error",
                        "message": "Agente não encontrado"
                    }
                    
        except Exception as e:
            logger.error(f"❌ Erro ao obter agente: {e}")
            return {
                "status": "error",
                "message": f"Erro ao obter agente: {str(e)}"
            }
    
    async def delete_agent_config(self, agent_id: int) -> Dict[str, Any]:
        """Deletar configuração de agente"""
        try:
            async with chamados_service.pool.acquire() as conn:
                result = await conn.fetchrow("""
                    DELETE FROM config_ia
                    WHERE id = $1
                    RETURNING id, nome
                """, agent_id)
                
                if result:
                    return {
                        "status": "success",
                        "message": f"Agente '{result['nome']}' deletado com sucesso"
                    }
                else:
                    return {
                        "status": "error",
                        "message": "Agente não encontrado"
                    }
                    
        except Exception as e:
            logger.error(f"❌ Erro ao deletar agente: {e}")
            return {
                "status": "error",
                "message": f"Erro ao deletar agente: {str(e)}"
            }
    
    async def deploy_agent(self, agent_id: int) -> Dict[str, Any]:
        """Deploy agente (ativar no sistema)"""
        try:
            async with chamados_service.pool.acquire() as conn:
                result = await conn.fetchrow("""
                    UPDATE config_ia 
                    SET active = true, updated_at = $2
                    WHERE id = $1
                    RETURNING id, nome, active
                """, agent_id, datetime.now())
                
                if result:
                    return {
                        "status": "success",
                        "message": f"Agente '{result['nome']}' ativado com sucesso",
                        "agent": {
                            "id": result["id"],
                            "nome": result["nome"],
                            "active": result["active"]
                        }
                    }
                else:
                    return {
                        "status": "error",
                        "message": "Agente não encontrado"
                    }
                    
        except Exception as e:
            logger.error(f"❌ Erro ao fazer deploy do agente: {e}")
            return {
                "status": "error",
                "message": f"Erro ao fazer deploy: {str(e)}"
            }
    
    async def get_agent_analytics(self, agent_id: int, days: int = 30) -> Dict[str, Any]:
        """Obter analytics de um agente"""
        try:
            async with chamados_service.pool.acquire() as conn:
                # Buscar métricas do agente
                metrics = await conn.fetchrow(f"""
                    SELECT 
                        COUNT(*) as total_interactions,
                        AVG(response_time) as avg_response_time,
                        COUNT(CASE WHEN success = true THEN 1 END) as successful_interactions,
                        COUNT(CASE WHEN success = false THEN 1 END) as failed_interactions,
                        AVG(tokens_used) as avg_tokens,
                        SUM(cost) as total_cost
                    FROM agent_interactions 
                    WHERE agent_id = $1 
                    AND created_at >= NOW() - INTERVAL '{days} days'
                """, agent_id)
                
                # Buscar distribuição por categoria
                categories = await conn.fetch(f"""
                    SELECT category, COUNT(*) as count
                    FROM agent_interactions 
                    WHERE agent_id = $1 
                    AND created_at >= NOW() - INTERVAL '{days} days'
                    GROUP BY category
                    ORDER BY count DESC
                """, agent_id)
                
                # Buscar performance por dia
                daily_performance = await conn.fetch(f"""
                    SELECT 
                        DATE(created_at) as date,
                        COUNT(*) as interactions,
                        AVG(response_time) as avg_response_time,
                        COUNT(CASE WHEN success = true THEN 1 END) as successful
                    FROM agent_interactions 
                    WHERE agent_id = $1 
                    AND created_at >= NOW() - INTERVAL '{days} days'
                    GROUP BY DATE(created_at)
                    ORDER BY date DESC
                """, agent_id)
                
                return {
                    "status": "success",
                    "analytics": {
                        "overview": dict(metrics) if metrics else {},
                        "categories": [dict(row) for row in categories],
                        "daily_performance": [dict(row) for row in daily_performance]
                    }
                }
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter analytics: {e}")
            return {
                "status": "error",
                "message": f"Erro ao obter analytics: {str(e)}"
            }
    
    async def create_agent_version(self, agent_id: int, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Criar nova versão de um agente"""
        try:
            async with chamados_service.pool.acquire() as conn:
                # Buscar agente atual
                current_agent = await conn.fetchrow("""
                    SELECT * FROM config_ia WHERE id = $1
                """, agent_id)
                
                if not current_agent:
                    return {
                        "status": "error",
                        "message": "Agente não encontrado"
                    }
                
                # Criar nova versão
                result = await conn.fetchrow("""
                    INSERT INTO config_ia (
                        prefeitura_id, nome, provider, config, active, created_at
                    ) VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING id, nome, provider, config, active, created_at
                """, current_agent["prefeitura_id"], config_data.get("name"), 
                    config_data.get("provider"), json.dumps(config_data), 
                    False, datetime.now())
                
                return {
                    "status": "success",
                    "message": "Nova versão criada com sucesso",
                    "version": {
                        "id": result["id"],
                        "nome": result["nome"],
                        "provider": result["provider"],
                        "created_at": result["created_at"].isoformat()
                    }
                }
                
        except Exception as e:
            logger.error(f"❌ Erro ao criar versão: {e}")
            return {
                "status": "error",
                "message": f"Erro ao criar versão: {str(e)}"
            }
    
    async def run_agent_test_suite(self, agent_id: int, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Executar suite de testes para um agente"""
        try:
            # Buscar configuração do agente
            agent_result = await self.get_agent_config(agent_id)
            
            if agent_result["status"] != "success":
                return agent_result
            
            agent_config = agent_result["agent"]["config"]
            results = []
            
            for test_case in test_cases:
                test_result = await self.test_agent_config(
                    agent_config, 
                    test_case.get("message", "")
                )
                
                results.append({
                    "test_case": test_case,
                    "result": test_result,
                    "passed": test_result["status"] == "success"
                })
            
            # Calcular métricas gerais
            total_tests = len(results)
            passed_tests = sum(1 for r in results if r["passed"])
            success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
            
            return {
                "status": "success",
                "test_results": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": total_tests - passed_tests,
                    "success_rate": success_rate,
                    "results": results
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao executar testes: {e}")
            return {
                "status": "error",
                "message": f"Erro ao executar testes: {str(e)}"
            }
    
    async def integrate_with_chatwoot(self, agent_id: int, chatwoot_config: Dict[str, Any]) -> Dict[str, Any]:
        """Integrar agente com Chatwoot"""
        try:
            async with chamados_service.pool.acquire() as conn:
                # Atualizar configuração do agente com dados do Chatwoot
                result = await conn.fetchrow("""
                    UPDATE config_ia 
                    SET config = config || $2, updated_at = $3
                    WHERE id = $1
                    RETURNING id, nome, config
                """, agent_id, json.dumps({
                    "chatwoot_integration": chatwoot_config,
                    "integrated_at": datetime.now().isoformat()
                }), datetime.now())
                
                if result:
                    return {
                        "status": "success",
                        "message": "Agente integrado com Chatwoot com sucesso",
                        "integration": {
                            "agent_id": result["id"],
                            "agent_name": result["nome"],
                            "chatwoot_config": chatwoot_config
                        }
                    }
                else:
                    return {
                        "status": "error",
                        "message": "Agente não encontrado"
                    }
                    
        except Exception as e:
            logger.error(f"❌ Erro ao integrar com Chatwoot: {e}")
            return {
                "status": "error",
                "message": f"Erro ao integrar com Chatwoot: {str(e)}"
            }
    
    async def get_agent_performance_metrics(self, agent_id: int) -> Dict[str, Any]:
        """Obter métricas de performance detalhadas"""
        try:
            async with chamados_service.pool.acquire() as conn:
                # Métricas gerais
                general_metrics = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_requests,
                        AVG(response_time) as avg_response_time,
                        MIN(response_time) as min_response_time,
                        MAX(response_time) as max_response_time,
                        COUNT(CASE WHEN success = true THEN 1 END) as successful_requests,
                        COUNT(CASE WHEN success = false THEN 1 END) as failed_requests,
                        AVG(tokens_used) as avg_tokens_per_request,
                        SUM(cost) as total_cost
                    FROM agent_interactions 
                    WHERE agent_id = $1
                """, agent_id)
                
                # Performance por hora do dia
                hourly_performance = await conn.fetch("""
                    SELECT 
                        EXTRACT(HOUR FROM created_at) as hour,
                        COUNT(*) as requests,
                        AVG(response_time) as avg_response_time,
                        COUNT(CASE WHEN success = true THEN 1 END) as successful
                    FROM agent_interactions 
                    WHERE agent_id = $1
                    GROUP BY EXTRACT(HOUR FROM created_at)
                    ORDER BY hour
                """, agent_id)
                
                # Top queries mais comuns
                top_queries = await conn.fetch("""
                    SELECT 
                        user_message,
                        COUNT(*) as frequency,
                        AVG(response_time) as avg_response_time,
                        COUNT(CASE WHEN success = true THEN 1 END) as successful
                    FROM agent_interactions 
                    WHERE agent_id = $1
                    GROUP BY user_message
                    ORDER BY frequency DESC
                    LIMIT 10
                """, agent_id)
                
                return {
                    "status": "success",
                    "metrics": {
                        "general": dict(general_metrics) if general_metrics else {},
                        "hourly_performance": [dict(row) for row in hourly_performance],
                        "top_queries": [dict(row) for row in top_queries]
                    }
                }
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter métricas de performance: {e}")
            return {
                "status": "error",
                "message": f"Erro ao obter métricas: {str(e)}"
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
