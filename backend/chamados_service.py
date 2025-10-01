"""
Serviço para gerenciamento de chamados cidadãos
"""
import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from decimal import Decimal
import asyncpg
from .models import (
    Cidadao, Chamado, Time, CategoriaChamado, InteracaoChamado,
    CriarChamadoRequest, CriarChamadoResponse,
    CadastrarCidadaoRequest, CadastrarCidadaoResponse,
    ConsultarChamadoRequest, ConsultarChamadoResponse
)

logger = logging.getLogger(__name__)


class ChamadosService:
    """Serviço principal para gerenciamento de chamados"""
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.pool = None
    
    async def init_db(self):
        """Inicializar pool de conexões"""
        if not self.database_url:
            raise ValueError("DATABASE_URL não configurada")
        
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
            logger.info("✅ Pool de conexões PostgreSQL criado com sucesso")
            
            # Executar migration se necessário
            await self._run_migration()
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar pool PostgreSQL: {e}")
            raise
    
    async def _run_migration(self):
        """Executar migration do sistema de chamados"""
        try:
            # Verificar se tabela já existe
            async with self.pool.acquire() as conn:
                result = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'prefeituras'
                    )
                """)
                
                if not result:
                    logger.info("🚀 Executando migration do sistema de chamados...")
                    
                    # Ler e executar migration
                    migration_file = os.path.join(
                        os.path.dirname(__file__), 
                        "migrations", 
                        "001_create_chamados_system.sql"
                    )
                    
                    if os.path.exists(migration_file):
                        with open(migration_file, 'r', encoding='utf-8') as f:
                            migration_sql = f.read()
                        
                        await conn.execute(migration_sql)
                        logger.info("✅ Migration executada com sucesso")
                    else:
                        logger.warning("⚠️ Arquivo de migration não encontrado")
                else:
                    logger.info("✅ Tabelas do sistema de chamados já existem")
                    
        except Exception as e:
            logger.error(f"❌ Erro ao executar migration: {e}")
            raise
    
    async def close(self):
        """Fechar pool de conexões"""
        if self.pool:
            await self.pool.close()
            logger.info("✅ Pool PostgreSQL fechado")
    
    # ========================================
    # MÉTODOS PARA CIDADÃOS
    # ========================================
    
    async def cadastrar_cidadao(self, request: CadastrarCidadaoRequest, prefeitura_id: int = 1) -> CadastrarCidadaoResponse:
        """Cadastrar novo cidadão"""
        try:
            async with self.pool.acquire() as conn:
                # Verificar se cidadão já existe
                existing = await conn.fetchrow(
                    """
                    SELECT c.id,
                           e.id AS endereco_id
                    FROM cidadaos c
                    LEFT JOIN LATERAL (
                        SELECT id
                        FROM cidadao_enderecos ce
                        WHERE ce.cidadao_id = c.id
                        ORDER BY ce.is_principal DESC, ce.created_at DESC
                        LIMIT 1
                    ) e ON TRUE
                    WHERE c.telefone = $1
                      AND c.prefeitura_id = $2
                      AND c.active = TRUE
                    """,
                    request.telefone,
                    prefeitura_id,
                )

                if existing:
                    await conn.execute(
                        """
                        UPDATE cidadaos SET
                            nome = $1,
                            cpf = $2,
                            email = $3,
                            data_nascimento = $4,
                            genero = $5,
                            updated_at = NOW()
                        WHERE id = $6
                        """,
                        request.nome,
                        request.cpf,
                        request.email,
                        request.data_nascimento,
                        request.genero,
                        existing["id"],
                    )

                    if existing["endereco_id"]:
                        await conn.execute(
                            """
                            UPDATE cidadao_enderecos SET
                                cep = $1,
                                logradouro = $2,
                                numero = $3,
                                bairro = $4,
                                cidade = $5,
                                estado = $6,
                                complemento = $7,
                                updated_at = NOW()
                            WHERE id = $8
                            """,
                            request.cep,
                            request.endereco,
                            request.numero,
                            request.bairro,
                            request.cidade,
                            request.estado,
                            request.complemento,
                            existing["endereco_id"],
                        )
                    else:
                        await conn.execute(
                            """
                            INSERT INTO cidadao_enderecos (
                                cidadao_id, cep, logradouro, numero, bairro,
                                cidade, estado, complemento, is_principal,
                                created_at
                            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, TRUE, NOW())
                            """,
                            existing["id"],
                            request.cep,
                            request.endereco,
                            request.numero,
                            request.bairro,
                            request.cidade,
                            request.estado,
                            request.complemento,
                        )

                    cidadao_data = await conn.fetchrow(
                        """
                        SELECT
                            c.*,
                            e.cep,
                            e.logradouro,
                            e.numero,
                            e.bairro,
                            e.cidade,
                            e.estado,
                            e.complemento
                        FROM cidadaos c
                        LEFT JOIN cidadao_enderecos e ON e.cidadao_id = c.id
                                                           AND e.is_principal = TRUE
                        WHERE c.id = $1
                        """,
                        existing["id"],
                    )

                    # Converter config se necessário
                    cidadao_dict = dict(cidadao_data)
                    if isinstance(cidadao_dict.get('config'), str):
                        try:
                            import json
                            cidadao_dict['config'] = json.loads(cidadao_dict['config'])
                        except:
                            cidadao_dict['config'] = {}
                    
                    return CadastrarCidadaoResponse(
                        status="success",
                        cidadao=Cidadao(
                            **cidadao_dict,
                            endereco=request.endereco,
                            numero=request.numero,
                            bairro=request.bairro,
                            cidade=request.cidade,
                            estado=request.estado,
                            cep=request.cep,
                            complemento=request.complemento,
                        ),
                        message="Dados do cidadão atualizados com sucesso",
                    )
                else:
                    # Inserir novo cidadão
                    cidadao_data = await conn.fetchrow("""
                        INSERT INTO cidadaos (
                            prefeitura_id, nome, cpf, telefone, email,
                            data_nascimento, genero
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                        RETURNING *
                        """,
                        prefeitura_id,
                        request.nome,
                        request.cpf,
                        request.telefone,
                        request.email,
                        request.data_nascimento,
                        request.genero,
                    )

                    await conn.execute(
                        """
                        INSERT INTO cidadao_enderecos (
                            cidadao_id, cep, logradouro, numero, bairro,
                            cidade, estado, complemento, is_principal,
                            created_at
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, TRUE, NOW())
                        """,
                        cidadao_data["id"],
                        request.cep,
                        request.endereco,
                        request.numero,
                        request.bairro,
                        request.cidade,
                        request.estado,
                        request.complemento,
                    )
                    
                    # Converter config se necessário
                    cidadao_dict = dict(cidadao_data)
                    if isinstance(cidadao_dict.get('config'), str):
                        try:
                            import json
                            cidadao_dict['config'] = json.loads(cidadao_dict['config'])
                        except:
                            cidadao_dict['config'] = {}
                    
                    return CadastrarCidadaoResponse(
                        status="success",
                        cidadao=Cidadao(
                            **cidadao_dict,
                            endereco=request.endereco,
                            numero=request.numero,
                            bairro=request.bairro,
                            cidade=request.cidade,
                            estado=request.estado,
                            cep=request.cep,
                            complemento=request.complemento,
                        ),
                        message="Cidadão cadastrado com sucesso",
                    )
                    
        except Exception as e:
            logger.error(f"❌ Erro ao cadastrar cidadão: {e}")
            return CadastrarCidadaoResponse(
                status="error",
                message=f"Erro ao cadastrar cidadão: {str(e)}"
            )
    
    async def buscar_cidadao_por_telefone(self, telefone: str, prefeitura_id: int = 1) -> Optional[Cidadao]:
        """Buscar cidadão por telefone"""
        try:
            async with self.pool.acquire() as conn:
                cidadao_data = await conn.fetchrow("""
                    SELECT * FROM cidadaos 
                    WHERE telefone = $1 AND prefeitura_id = $2 AND active = true
                """, telefone, prefeitura_id)
                
                if cidadao_data:
                    # Converter config se necessário
                    cidadao_dict = dict(cidadao_data)
                    if isinstance(cidadao_dict.get('config'), str):
                        try:
                            import json
                            cidadao_dict['config'] = json.loads(cidadao_dict['config'])
                        except:
                            cidadao_dict['config'] = {}
                    
                    return Cidadao(**cidadao_dict)
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao buscar cidadão: {e}")
            return None
    
    # ========================================
    # MÉTODOS PARA CHAMADOS
    # ========================================
    
    async def criar_chamado(self, request: CriarChamadoRequest, prefeitura_id: int = 1) -> CriarChamadoResponse:
        """Criar novo chamado"""
        try:
            async with self.pool.acquire() as conn:
                # Buscar cidadão
                cidadao = await self.buscar_cidadao_por_telefone(request.cidadao_telefone, prefeitura_id)
                if not cidadao:
                    return CriarChamadoResponse(
                        status="error",
                        message="Cidadão não encontrado. É necessário cadastrar primeiro."
                    )
                
                # Categorizar automaticamente
                categoria = await self._categorizar_chamado(request.titulo + " " + request.descricao, prefeitura_id)
                
                # Gerar protocolo
                protocolo = await self._gerar_protocolo(categoria['time_id'] if categoria else None, conn)
                
                # Calcular SLA deadline
                sla_deadline = None
                if categoria:
                    sla_deadline = datetime.now() + timedelta(hours=categoria['sla_horas'])
                
                # Inserir chamado
                chamado_data = await conn.fetchrow("""
                    INSERT INTO chamados (
                        prefeitura_id, protocolo, cidadao_id, categoria_id, time_id,
                        titulo, descricao, endereco_ocorrencia, latitude, longitude,
                        prioridade, sla_deadline, fonte
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                    RETURNING *
                """, prefeitura_id, protocolo, cidadao.id, categoria['id'] if categoria else None,
                     categoria['time_id'] if categoria else None, request.titulo, request.descricao,
                     request.endereco_ocorrencia, request.latitude, request.longitude,
                     categoria['prioridade'] if categoria else 'normal', sla_deadline, request.fonte)
                
                # Registrar interação
                await self._registrar_interacao(
                    chamado_data['id'], None, 'mensagem', 
                    f"Chamado criado automaticamente via {request.fonte}", {}
                )
                
                return CriarChamadoResponse(
                    status="success",
                    chamado=Chamado(**chamado_data),
                    protocolo=protocolo,
                    message=f"Chamado criado com sucesso! Protocolo: {protocolo}"
                )
                
        except Exception as e:
            logger.error(f"❌ Erro ao criar chamado: {e}")
            return CriarChamadoResponse(
                status="error",
                message=f"Erro ao criar chamado: {str(e)}"
            )
    
    async def consultar_chamado(self, request: ConsultarChamadoRequest, prefeitura_id: int = 1) -> ConsultarChamadoResponse:
        """Consultar chamado por protocolo ou telefone"""
        try:
            async with self.pool.acquire() as conn:
                if request.protocolo:
                    # Buscar por protocolo
                    chamado_data = await conn.fetchrow("""
                        SELECT c.*, ci.nome as cidadao_nome, ci.telefone as cidadao_telefone,
                               cat.nome as categoria_nome, t.nome as time_nome
                        FROM chamados c
                        JOIN cidadaos ci ON c.cidadao_id = ci.id
                        LEFT JOIN categorias_chamados cat ON c.categoria_id = cat.id
                        LEFT JOIN times t ON c.time_id = t.id
                        WHERE c.protocolo = $1 AND c.prefeitura_id = $2
                    """, request.protocolo, prefeitura_id)
                    
                elif request.telefone_cidadao:
                    # Buscar último chamado do cidadão
                    chamado_data = await conn.fetchrow("""
                        SELECT c.*, ci.nome as cidadao_nome, ci.telefone as cidadao_telefone,
                               cat.nome as categoria_nome, t.nome as time_nome
                        FROM chamados c
                        JOIN cidadaos ci ON c.cidadao_id = ci.id
                        LEFT JOIN categorias_chamados cat ON c.categoria_id = cat.id
                        LEFT JOIN times t ON c.time_id = t.id
                        WHERE ci.telefone = $1 AND c.prefeitura_id = $2
                        ORDER BY c.created_at DESC
                        LIMIT 1
                    """, request.telefone_cidadao, prefeitura_id)
                else:
                    return ConsultarChamadoResponse(
                        status="error",
                        message="É necessário informar protocolo ou telefone do cidadão"
                    )
                
                if not chamado_data:
                    return ConsultarChamadoResponse(
                        status="error",
                        message="Chamado não encontrado"
                    )
                
                # Buscar dados completos
                cidadao = await self.buscar_cidadao_por_telefone(chamado_data['cidadao_telefone'], prefeitura_id)
                
                categoria = None
                if chamado_data['categoria_id']:
                    categoria_data = await conn.fetchrow("""
                        SELECT * FROM categorias_chamados WHERE id = $1
                    """, chamado_data['categoria_id'])
                    if categoria_data:
                        categoria = CategoriaChamado(**categoria_data)
                
                time = None
                if chamado_data['time_id']:
                    time_data = await conn.fetchrow("""
                        SELECT * FROM times WHERE id = $1
                    """, chamado_data['time_id'])
                    if time_data:
                        time = Time(**time_data)
                
                return ConsultarChamadoResponse(
                    status="success",
                    chamado=Chamado(**chamado_data),
                    cidadao=cidadao,
                    categoria=categoria,
                    time=time,
                    message="Chamado encontrado com sucesso"
                )
                
        except Exception as e:
            logger.error(f"❌ Erro ao consultar chamado: {e}")
            return ConsultarChamadoResponse(
                status="error",
                message=f"Erro ao consultar chamado: {str(e)}"
            )
    
    # ========================================
    # MÉTODOS AUXILIARES
    # ========================================
    
    async def _categorizar_chamado(self, texto: str, prefeitura_id: int) -> Optional[Dict[str, Any]]:
        """Categorizar chamado baseado no texto"""
        try:
            async with self.pool.acquire() as conn:
                # Buscar categorias com palavras-chave
                categorias = await conn.fetch("""
                    SELECT cc.*, t.nome as time_nome
                    FROM categorias_chamados cc
                    JOIN times t ON cc.time_id = t.id
                    WHERE cc.prefeitura_id = $1 AND cc.active = true
                """, prefeitura_id)
                
                texto_lower = texto.lower()
                melhor_match = None
                melhor_score = 0
                
                for categoria in categorias:
                    score = 0
                    keywords = categoria['keywords'] or []
                    
                    for keyword in keywords:
                        if keyword.lower() in texto_lower:
                            score += 1
                    
                    if score > melhor_score:
                        melhor_score = score
                        melhor_match = dict(categoria)
                
                return melhor_match if melhor_match and melhor_score > 0 else None
                
        except Exception as e:
            logger.error(f"❌ Erro ao categorizar chamado: {e}")
            return None
    
    async def _gerar_protocolo(self, time_id: Optional[int], conn) -> str:
        """Gerar protocolo único"""
        try:
            if time_id:
                # Gerar protocolo com prefixo do time
                protocolo = await conn.fetchval("""
                    SELECT gerar_protocolo_chamado($1)
                """, time_id)
                return protocolo
            else:
                # Protocolo genérico
                ano = datetime.now().year
                sequencial = await conn.fetchval("""
                    SELECT COALESCE(MAX(CAST(SUBSTRING(protocolo FROM '\d+$') AS INT)), 0) + 1
                    FROM chamados 
                    WHERE protocolo LIKE 'GERAL-' || $1 || '-%'
                """, ano)
                return f"GERAL-{ano}-{sequencial:03d}"
                
        except Exception as e:
            logger.error(f"❌ Erro ao gerar protocolo: {e}")
            # Fallback
            return f"CHAMADO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    async def _registrar_interacao(self, chamado_id: int, agente_id: Optional[int], 
                                 tipo: str, conteudo: str, metadata: Dict[str, Any]):
        """Registrar interação no histórico do chamado"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO interacoes_chamado (chamado_id, agente_id, tipo, conteudo, metadata)
                    VALUES ($1, $2, $3, $4, $5)
                """, chamado_id, agente_id, tipo, conteudo, metadata)
                
        except Exception as e:
            logger.error(f"❌ Erro ao registrar interação: {e}")
    
    # ========================================
    # MÉTODOS PARA RELATÓRIOS
    # ========================================
    
    async def obter_metricas_dashboard(self, prefeitura_id: int = 1) -> Dict[str, Any]:
        """Obter métricas para dashboard"""
        try:
            async with self.pool.acquire() as conn:
                metrics = await conn.fetchrow("""
                    SELECT * FROM vw_dashboard_metrics WHERE prefeitura_id = $1
                """, prefeitura_id)
                
                if metrics:
                    return dict(metrics)
                else:
                    return {
                        'prefeitura_id': prefeitura_id,
                        'total_chamados': 0,
                        'chamados_abertos': 0,
                        'chamados_andamento': 0,
                        'chamados_resolvidos': 0,
                        'chamados_cancelados': 0,
                        'tempo_medio_resolucao_horas': 0
                    }
                    
        except Exception as e:
            logger.error(f"❌ Erro ao obter métricas: {e}")
            return {}
    
    async def listar_cidadaos(self, prefeitura_id: int = 1):
        """Listar todos os cidadãos cadastrados"""
        try:
            async with self.pool.acquire() as conn:
                cidadaos_data = await conn.fetch(
                    """
                    SELECT
                        c.id,
                        c.nome,
                        c.telefone,
                        c.email,
                        c.chatwoot_contact_id,
                        c.created_at,
                        c.updated_at,
                        e.cep,
                        e.logradouro,
                        e.numero,
                        e.bairro,
                        e.cidade,
                        e.estado,
                        e.complemento
                    FROM cidadaos c
                    LEFT JOIN LATERAL (
                        SELECT *
                        FROM cidadao_enderecos ce
                        WHERE ce.cidadao_id = c.id
                        ORDER BY ce.is_principal DESC, ce.created_at DESC
                        LIMIT 1
                    ) e ON TRUE
                    WHERE c.prefeitura_id = $1 AND c.active = true
                    ORDER BY c.created_at DESC
                    """,
                    prefeitura_id,
                )
                
                cidadaos = []
                for row in cidadaos_data:
                    cidadaos.append({
                        "id": row["id"],
                        "nome": row["nome"],
                        "telefone": row["telefone"],
                        "email": row["email"],
                        "endereco": {
                            "cep": row["cep"],
                            "logradouro": row["logradouro"],
                            "numero": row["numero"],
                            "bairro": row["bairro"],
                            "cidade": row["cidade"],
                            "estado": row["estado"],
                            "complemento": row["complemento"],
                        },
                        "chatwoot_contact_id": row["chatwoot_contact_id"],
                        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                        "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None
                    })
                
                return cidadaos
                
        except Exception as e:
            logger.error(f"❌ Erro ao listar cidadãos: {e}")
            return []
    
    async def listar_chamados(self, prefeitura_id: int = 1):
        """Listar todos os chamados"""
        try:
            async with self.pool.acquire() as conn:
                chamados_data = await conn.fetch("""
                    SELECT c.id, c.protocolo, c.titulo, c.descricao, c.status, c.prioridade,
                           c.created_at, c.updated_at, c.resolved_at,
                           ci.nome as cidadao_nome, ci.telefone as cidadao_telefone,
                           cat.nome as categoria_nome, t.nome as time_nome
                    FROM chamados c
                    JOIN cidadaos ci ON c.cidadao_id = ci.id
                    LEFT JOIN categorias_chamados cat ON c.categoria_id = cat.id
                    LEFT JOIN times t ON c.time_id = t.id
                    WHERE c.prefeitura_id = $1
                    ORDER BY c.created_at DESC
                """, prefeitura_id)
                
                chamados = []
                for row in chamados_data:
                    chamados.append({
                        "id": row["id"],
                        "protocolo": row["protocolo"],
                        "titulo": row["titulo"],
                        "descricao": row["descricao"],
                        "status": row["status"],
                        "prioridade": row["prioridade"],
                        "cidadao_nome": row["cidadao_nome"],
                        "cidadao_telefone": row["cidadao_telefone"],
                        "categoria_nome": row["categoria_nome"],
                        "time_nome": row["time_nome"],
                        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                        "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
                        "resolved_at": row["resolved_at"].isoformat() if row["resolved_at"] else None
                    })
                
                return chamados
                
        except Exception as e:
            logger.error(f"❌ Erro ao listar chamados: {e}")
            return []


# Instância global do serviço
chamados_service = ChamadosService()
