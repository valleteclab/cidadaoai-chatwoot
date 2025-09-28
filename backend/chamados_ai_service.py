"""
Serviço de IA especializado para sistema de chamados cidadãos
"""
import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from .ai_agent import CidadaoAIAgent
from .chamados_service import chamados_service
from .models import Cidadao, Chamado

logger = logging.getLogger(__name__)


class ChamadosAIService:
    """Serviço de IA para gerenciamento de chamados"""
    
    def __init__(self):
        self.ai_agent = CidadaoAIAgent()
        self.conversation_states = {}  # Estados das conversas
    
    def is_available(self) -> bool:
        """Verificar se IA está disponível"""
        return self.ai_agent.is_available()
    
    async def process_citizen_message(self, message: str, conversation_id: int, 
                                    contact_info: Dict[str, Any] = None) -> Optional[str]:
        """Processar mensagem do cidadão com lógica de chamados"""
        try:
            logger.info(f"🤖 PROCESSANDO MENSAGEM CIDADÃO - Conversa {conversation_id}")
            
            # Obter estado da conversa
            state = self.conversation_states.get(conversation_id, {})
            current_step = state.get('step', 'initial')
            
            # Extrair telefone do contato
            telefone = contact_info.get('phone_number', '') if contact_info else ''
            
            if current_step == 'initial':
                return await self._handle_initial_message(message, telefone, conversation_id, contact_info)
            
            elif current_step == 'collecting_data':
                return await self._handle_data_collection(message, telefone, conversation_id, contact_info, state)
            
            elif current_step == 'collecting_issue':
                return await self._handle_issue_collection(message, telefone, conversation_id, contact_info, state)
            
            elif current_step == 'confirming_category':
                return await self._handle_category_confirmation(message, telefone, conversation_id, contact_info, state)
            
            elif current_step == 'collecting_address':
                return await self._handle_address_collection(message, telefone, conversation_id, contact_info, state)
            
            elif current_step == 'ticket_created':
                return await self._handle_ticket_created(message, telefone, conversation_id, contact_info, state)
            
            else:
                # Estado desconhecido, voltar ao início
                self.conversation_states[conversation_id] = {'step': 'initial'}
                return await self._handle_initial_message(message, telefone, conversation_id, contact_info)
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar mensagem do cidadão: {e}")
            return "Desculpe, ocorreu um erro interno. Por favor, tente novamente."
    
    async def _handle_initial_message(self, message: str, telefone: str, 
                                    conversation_id: int, contact_info: Dict[str, Any]) -> str:
        """Processar mensagem inicial"""
        try:
            # Verificar se é consulta de status
            if any(word in message.lower() for word in ['status', 'protocolo', 'chamado', 'situação']):
                return await self._handle_status_query(message, telefone, conversation_id)
            
            # Verificar se cidadão já está cadastrado
            cidadao = await chamados_service.buscar_cidadao_por_telefone(telefone)
            
            if cidadao:
                # Cidadão já cadastrado, ir direto para coleta do problema
                self.conversation_states[conversation_id] = {
                    'step': 'collecting_issue',
                    'cidadao': cidadao
                }
                
                return f"""Olá {cidadao.nome}! 👋

Vejo que você já está cadastrado em nosso sistema. 

Como posso ajudá-lo hoje? Por favor, descreva o problema ou solicitação que gostaria de registrar."""
            else:
                # Cidadão não cadastrado, iniciar processo de cadastro
                self.conversation_states[conversation_id] = {
                    'step': 'collecting_data',
                    'dados_coletados': {}
                }
                
                return """Olá! 👋 Bem-vindo ao sistema de atendimento da Prefeitura!

Para abrir um chamado, preciso primeiro cadastrá-lo em nosso sistema.

Por favor, me informe seu **nome completo**:"""
                
        except Exception as e:
            logger.error(f"❌ Erro no tratamento de mensagem inicial: {e}")
            return "Desculpe, ocorreu um erro. Por favor, tente novamente."
    
    async def _handle_data_collection(self, message: str, telefone: str, 
                                    conversation_id: int, contact_info: Dict[str, Any], 
                                    state: Dict[str, Any]) -> str:
        """Processar coleta de dados do cidadão"""
        try:
            dados = state.get('dados_coletados', {})
            
            if 'nome' not in dados:
                # Coletando nome
                dados['nome'] = message.strip()
                dados['telefone'] = telefone
                
                self.conversation_states[conversation_id]['dados_coletados'] = dados
                
                return f"""Perfeito, {dados['nome']}! 😊

Agora preciso do seu **CPF** (apenas os números):"""
            
            elif 'cpf' not in dados:
                # Coletando CPF
                cpf = ''.join(filter(str.isdigit, message))
                if len(cpf) == 11:
                    dados['cpf'] = cpf
                    self.conversation_states[conversation_id]['dados_coletados'] = dados
                    
                    return """Ótimo! Agora me informe seu **endereço completo** (rua, número, bairro):"""
                else:
                    return """CPF inválido. Por favor, digite apenas os 11 números do seu CPF:"""
            
            elif 'endereco' not in dados:
                # Coletando endereço
                dados['endereco'] = message.strip()
                self.conversation_states[conversation_id]['dados_coletados'] = dados
                
                return """Agora me informe seu **e-mail** (opcional - pode digitar "não tenho"):"""
            
            elif 'email' not in dados:
                # Coletando email
                email = message.strip().lower()
                if email in ['não tenho', 'nao tenho', 'não', 'nao', '-', '']:
                    dados['email'] = None
                else:
                    dados['email'] = email
                
                # Cadastrar cidadão
                from .models import CadastrarCidadaoRequest
                
                request = CadastrarCidadaoRequest(
                    telefone=dados['telefone'],
                    nome=dados['nome'],
                    cpf=dados['cpf'],
                    email=dados['email'],
                    endereco=dados['endereco']
                )
                
                response = await chamados_service.cadastrar_cidadao(request)
                
                if response.status == "success":
                    # Cadastro realizado, ir para coleta do problema
                    self.conversation_states[conversation_id] = {
                        'step': 'collecting_issue',
                        'cidadao': response.cidadao
                    }
                    
                    return f"""✅ Cadastro realizado com sucesso!

Olá {response.cidadao.nome}, como posso ajudá-lo hoje? 

Por favor, descreva o problema ou solicitação que gostaria de registrar:"""
                else:
                    return f"❌ Erro ao cadastrar: {response.message}"
                    
        except Exception as e:
            logger.error(f"❌ Erro na coleta de dados: {e}")
            return "Desculpe, ocorreu um erro no cadastro. Por favor, tente novamente."
    
    async def _handle_issue_collection(self, message: str, telefone: str, 
                                     conversation_id: int, contact_info: Dict[str, Any], 
                                     state: Dict[str, Any]) -> str:
        """Processar coleta do problema/solicitação"""
        try:
            # Salvar descrição do problema
            self.conversation_states[conversation_id]['problema'] = message.strip()
            
            # Categorizar automaticamente
            from .chamados_service import chamados_service
            categoria = await chamados_service._categorizar_chamado(message, 1)
            
            if categoria:
                self.conversation_states[conversation_id].update({
                    'step': 'confirming_category',
                    'categoria_sugerida': categoria
                })
                
                return f"""Entendi! Analisando sua solicitação...

🔍 **Categoria sugerida**: {categoria['nome']}  
🏢 **Setor responsável**: {categoria['time_nome']}

Esta categorização está correta? (Digite "sim" ou "não")"""
            else:
                # Categoria não identificada, pedir para especificar
                self.conversation_states[conversation_id]['step'] = 'manual_category'
                
                return """Não consegui identificar automaticamente a categoria do seu chamado.

Por favor, me informe qual setor é responsável pelo seu problema:
- 🏗️ **Infraestrutura** (buraco, iluminação, esgoto)
- 🏥 **Saúde** (posto, médico, remédio)
- 🎓 **Educação** (escola, merenda, transporte)
- 🤝 **Assistência Social** (bolsa, benefício, cadastro)
- 🔨 **Obras** (construção, reforma, pavimentação)

Digite o nome do setor:"""
                
        except Exception as e:
            logger.error(f"❌ Erro na coleta do problema: {e}")
            return "Desculpe, ocorreu um erro. Por favor, tente novamente."
    
    async def _handle_category_confirmation(self, message: str, telefone: str, 
                                          conversation_id: int, contact_info: Dict[str, Any], 
                                          state: Dict[str, Any]) -> str:
        """Processar confirmação de categoria"""
        try:
            resposta = message.strip().lower()
            
            if resposta in ['sim', 's', 'yes', 'y', 'correto', 'certo']:
                # Categoria confirmada, coletar endereço
                self.conversation_states[conversation_id]['step'] = 'collecting_address'
                
                return """✅ Perfeito! Categoria confirmada.

Agora preciso do **endereço onde ocorre o problema** (rua, número, bairro):"""
            
            elif resposta in ['não', 'nao', 'n', 'no', 'errado', 'incorreto']:
                # Categoria incorreta, pedir para especificar
                self.conversation_states[conversation_id]['step'] = 'manual_category'
                
                return """Entendi! Vamos especificar melhor.

Por favor, me informe qual setor é responsável pelo seu problema:
- 🏗️ **Infraestrutura** (buraco, iluminação, esgoto)
- 🏥 **Saúde** (posto, médico, remédio)
- 🎓 **Educação** (escola, merenda, transporte)
- 🤝 **Assistência Social** (bolsa, benefício, cadastro)
- 🔨 **Obras** (construção, reforma, pavimentação)

Digite o nome do setor:"""
            
            else:
                return """Por favor, responda "sim" ou "não" para confirmar a categoria:"""
                
        except Exception as e:
            logger.error(f"❌ Erro na confirmação de categoria: {e}")
            return "Desculpe, ocorreu um erro. Por favor, tente novamente."
    
    async def _handle_address_collection(self, message: str, telefone: str, 
                                       conversation_id: int, contact_info: Dict[str, Any], 
                                       state: Dict[str, Any]) -> str:
        """Processar coleta de endereço e criar chamado"""
        try:
            endereco = message.strip()
            
            # Criar chamado
            from .models import CriarChamadoRequest
            
            request = CriarChamadoRequest(
                cidadao_telefone=telefone,
                titulo=self._gerar_titulo_chamado(state.get('problema', '')),
                descricao=state.get('problema', ''),
                endereco_ocorrencia=endereco,
                fonte='whatsapp'
            )
            
            response = await chamados_service.criar_chamado(request)
            
            if response.status == "success":
                # Chamado criado com sucesso
                self.conversation_states[conversation_id] = {
                    'step': 'ticket_created',
                    'protocolo': response.protocolo,
                    'chamado': response.chamado
                }
                
                return f"""🎉 **Chamado criado com sucesso!**

📋 **Protocolo**: {response.protocolo}
📝 **Descrição**: {response.chamado.titulo}
🏢 **Setor**: {state.get('categoria_sugerida', {}).get('time_nome', 'A definir')}
📍 **Local**: {endereco}

⏰ **Previsão de atendimento**: {self._calcular_previsao(state.get('categoria_sugerida', {}).get('sla_horas', 72))}

Você pode consultar o status deste chamado a qualquer momento digitando: **status {response.protocolo}**

Precisa de mais alguma coisa? 😊"""
            else:
                return f"❌ Erro ao criar chamado: {response.message}"
                
        except Exception as e:
            logger.error(f"❌ Erro ao criar chamado: {e}")
            return "Desculpe, ocorreu um erro ao criar o chamado. Por favor, tente novamente."
    
    async def _handle_status_query(self, message: str, telefone: str, conversation_id: int) -> str:
        """Processar consulta de status"""
        try:
            from .models import ConsultarChamadoRequest
            
            # Extrair protocolo da mensagem se presente
            protocolo = None
            for word in message.split():
                if '-' in word and len(word) > 5:
                    protocolo = word.upper()
                    break
            
            request = ConsultarChamadoRequest(
                protocolo=protocolo,
                telefone_cidadao=telefone if not protocolo else None
            )
            
            response = await chamados_service.consultar_chamado(request)
            
            if response.status == "success" and response.chamado:
                chamado = response.chamado
                
                status_emoji = {
                    'aberto': '🔴',
                    'em_andamento': '🟡', 
                    'resolvido': '🟢',
                    'cancelado': '⚫'
                }
                
                return f"""📋 **Status do Chamado**

🔖 **Protocolo**: {chamado.protocolo}
📝 **Descrição**: {chamado.titulo}
{status_emoji.get(chamado.status, '❓')} **Status**: {chamado.status.replace('_', ' ').title()}
🏢 **Setor**: {response.time.nome if response.time else 'A definir'}
📅 **Data**: {chamado.created_at.strftime('%d/%m/%Y %H:%M') if chamado.created_at else 'N/A'}

{f'✅ **Resolvido em**: {chamado.resolved_at.strftime("%d/%m/%Y %H:%M")}' if chamado.resolved_at else ''}

Para mais informações, entre em contato com nossa equipe! 😊"""
            else:
                return """❌ Chamado não encontrado.

Verifique se o protocolo está correto ou se você tem algum chamado em andamento.

Para criar um novo chamado, basta me enviar uma mensagem descrevendo seu problema! 😊"""
                
        except Exception as e:
            logger.error(f"❌ Erro ao consultar status: {e}")
            return "Desculpe, ocorreu um erro ao consultar o chamado. Por favor, tente novamente."
    
    async def _handle_ticket_created(self, message: str, telefone: str, 
                                   conversation_id: int, contact_info: Dict[str, Any], 
                                   state: Dict[str, Any]) -> str:
        """Processar mensagens após criação do chamado"""
        try:
            # Verificar se é consulta de status
            if any(word in message.lower() for word in ['status', 'protocolo', 'situação']):
                return await self._handle_status_query(message, telefone, conversation_id)
            
            # Verificar se quer criar novo chamado
            if any(word in message.lower() for word in ['novo', 'outro', 'problema', 'chamado']):
                self.conversation_states[conversation_id] = {'step': 'collecting_issue'}
                return """Ótimo! Vamos criar um novo chamado.

Por favor, descreva o problema ou solicitação:"""
            
            # Resposta padrão
            protocolo = state.get('protocolo', 'N/A')
            return f"""Seu chamado {protocolo} foi registrado com sucesso! 🎉

Se precisar de mais alguma coisa ou quiser criar outro chamado, é só me avisar! 😊"""
            
        except Exception as e:
            logger.error(f"❌ Erro após criação do chamado: {e}")
            return "Desculpe, ocorreu um erro. Por favor, tente novamente."
    
    def _gerar_titulo_chamado(self, descricao: str) -> str:
        """Gerar título baseado na descrição"""
        # Pegar as primeiras palavras da descrição
        palavras = descricao.split()[:8]
        titulo = ' '.join(palavras)
        
        if len(titulo) > 100:
            titulo = titulo[:97] + '...'
        
        return titulo or 'Chamado sem título'
    
    def _calcular_previsao(self, sla_horas: int) -> str:
        """Calcular previsão de atendimento"""
        from datetime import datetime, timedelta
        
        deadline = datetime.now() + timedelta(hours=sla_horas)
        
        if sla_horas <= 24:
            return f"{sla_horas}h úteis"
        elif sla_horas <= 72:
            return f"{sla_horas//24} dias úteis"
        else:
            return f"{sla_horas//168} semana(s)"


# Instância global do serviço
chamados_ai_service = ChamadosAIService()
