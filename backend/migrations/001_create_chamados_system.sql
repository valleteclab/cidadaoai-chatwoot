-- ========================================
-- MIGRATION 001: SISTEMA DE CHAMADOS CIDADÃOS
-- Data: 2024-12-28
-- Versão: 1.0
-- ========================================

-- 1. PREFEITURAS/CLIENTES (Caixas de Entrada)
CREATE TABLE IF NOT EXISTS prefeituras (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    chatwoot_account_id INT UNIQUE,
    chatwoot_inbox_id INT,
    whatsapp_number VARCHAR(20),
    config JSONB DEFAULT '{}',
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 2. TIMES/SECRETARIAS
CREATE TABLE IF NOT EXISTS times (
    id SERIAL PRIMARY KEY,
    prefeitura_id INT REFERENCES prefeituras(id) ON DELETE CASCADE,
    nome VARCHAR(100) NOT NULL,
    chatwoot_team_id INT,
    cor VARCHAR(7) DEFAULT '#4ECDC4',
    keywords TEXT[] DEFAULT '{}',
    responsavel_nome VARCHAR(255),
    responsavel_email VARCHAR(255),
    config JSONB DEFAULT '{}',
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 3. AGENTES (Humanos e IA)
CREATE TABLE IF NOT EXISTS agentes (
    id SERIAL PRIMARY KEY,
    prefeitura_id INT REFERENCES prefeituras(id) ON DELETE CASCADE,
    nome VARCHAR(255) NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('humano', 'ia_cadastro', 'ia_infraestrutura', 'ia_geral', 'ia_saude', 'ia_educacao')),
    chatwoot_agent_id INT,
    email VARCHAR(255),
    telefone VARCHAR(20),
    config JSONB DEFAULT '{}',
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 4. RELACIONAMENTO AGENTE-TIME
CREATE TABLE IF NOT EXISTS agente_times (
    id SERIAL PRIMARY KEY,
    agente_id INT REFERENCES agentes(id) ON DELETE CASCADE,
    time_id INT REFERENCES times(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member' CHECK (role IN ('member', 'admin')),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(agente_id, time_id)
);

-- 5. CIDADÃOS
CREATE TABLE IF NOT EXISTS cidadaos (
    id SERIAL PRIMARY KEY,
    prefeitura_id INT REFERENCES prefeituras(id) ON DELETE CASCADE,
    nome VARCHAR(255) NOT NULL,
    cpf VARCHAR(14) UNIQUE,
    telefone VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    endereco TEXT,
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    cep VARCHAR(10),
    chatwoot_contact_id INT,
    data_nascimento DATE,
    genero VARCHAR(20),
    config JSONB DEFAULT '{}',
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 6. CATEGORIAS DE CHAMADOS
CREATE TABLE IF NOT EXISTS categorias_chamados (
    id SERIAL PRIMARY KEY,
    prefeitura_id INT REFERENCES prefeituras(id) ON DELETE CASCADE,
    time_id INT REFERENCES times(id) ON DELETE CASCADE,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    keywords TEXT[] DEFAULT '{}',
    prioridade VARCHAR(20) DEFAULT 'normal' CHECK (prioridade IN ('baixa', 'normal', 'alta', 'urgente')),
    sla_horas INT DEFAULT 72,
    template_resposta TEXT,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 7. CHAMADOS/PROTOCOLOS
CREATE TABLE IF NOT EXISTS chamados (
    id SERIAL PRIMARY KEY,
    prefeitura_id INT REFERENCES prefeituras(id) ON DELETE CASCADE,
    protocolo VARCHAR(50) UNIQUE NOT NULL,
    cidadao_id INT REFERENCES cidadaos(id) ON DELETE CASCADE,
    categoria_id INT REFERENCES categorias_chamados(id),
    time_id INT REFERENCES times(id) ON DELETE CASCADE,
    chatwoot_conversation_id INT,
    
    -- Dados do chamado
    titulo VARCHAR(255) NOT NULL,
    descricao TEXT NOT NULL,
    endereco_ocorrencia TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    
    -- Status e fluxo
    status VARCHAR(50) DEFAULT 'aberto' CHECK (status IN ('aberto', 'em_andamento', 'resolvido', 'cancelado')),
    prioridade VARCHAR(20) DEFAULT 'normal' CHECK (prioridade IN ('baixa', 'normal', 'alta', 'urgente')),
    sla_deadline TIMESTAMP,
    
    -- Atribuições
    agente_responsavel_id INT REFERENCES agentes(id),
    agente_atribuido_por_id INT REFERENCES agentes(id),
    
    -- Metadados
    fonte VARCHAR(50) DEFAULT 'whatsapp' CHECK (fonte IN ('whatsapp', 'web', 'telefone', 'presencial')),
    tags TEXT[] DEFAULT '{}',
    anexos JSONB DEFAULT '[]',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP,
    
    -- Configurações
    config JSONB DEFAULT '{}'
);

-- 8. INTERAÇÕES/HISTÓRICO
CREATE TABLE IF NOT EXISTS interacoes_chamado (
    id SERIAL PRIMARY KEY,
    chamado_id INT REFERENCES chamados(id) ON DELETE CASCADE,
    agente_id INT REFERENCES agentes(id),
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('mensagem', 'atribuicao', 'status_change', 'comentario', 'resolucao')),
    conteudo TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- 9. TEMPLATES DE RESPOSTA
CREATE TABLE IF NOT EXISTS templates_resposta (
    id SERIAL PRIMARY KEY,
    prefeitura_id INT REFERENCES prefeituras(id) ON DELETE CASCADE,
    categoria_id INT REFERENCES categorias_chamados(id),
    nome VARCHAR(100) NOT NULL,
    template TEXT NOT NULL,
    variaveis JSONB DEFAULT '{}',
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 10. CONFIGURAÇÕES DE IA
CREATE TABLE IF NOT EXISTS config_ia (
    id SERIAL PRIMARY KEY,
    prefeitura_id INT REFERENCES prefeituras(id) ON DELETE CASCADE,
    agente_id INT REFERENCES agentes(id) ON DELETE CASCADE,
    nome VARCHAR(100) NOT NULL,
    prompt_system TEXT,
    config JSONB DEFAULT '{}',
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ========================================
-- ÍNDICES PARA PERFORMANCE
-- ========================================

CREATE INDEX IF NOT EXISTS idx_cidadaos_telefone ON cidadaos(telefone);
CREATE INDEX IF NOT EXISTS idx_cidadaos_cpf ON cidadaos(cpf);
CREATE INDEX IF NOT EXISTS idx_cidadaos_prefeitura ON cidadaos(prefeitura_id);
CREATE INDEX IF NOT EXISTS idx_cidadaos_chatwoot_contact ON cidadaos(chatwoot_contact_id);

CREATE INDEX IF NOT EXISTS idx_chamados_protocolo ON chamados(protocolo);
CREATE INDEX IF NOT EXISTS idx_chamados_cidadao ON chamados(cidadao_id);
CREATE INDEX IF NOT EXISTS idx_chamados_status ON chamados(status);
CREATE INDEX IF NOT EXISTS idx_chamados_prefeitura ON chamados(prefeitura_id);
CREATE INDEX IF NOT EXISTS idx_chamados_time ON chamados(time_id);
CREATE INDEX IF NOT EXISTS idx_chamados_created ON chamados(created_at);
CREATE INDEX IF NOT EXISTS idx_chamados_chatwoot_conversation ON chamados(chatwoot_conversation_id);

CREATE INDEX IF NOT EXISTS idx_interacoes_chamado ON interacoes_chamado(chamado_id);
CREATE INDEX IF NOT EXISTS idx_interacoes_created ON interacoes_chamado(created_at);

CREATE INDEX IF NOT EXISTS idx_categorias_keywords ON categorias_chamados USING GIN(keywords);
CREATE INDEX IF NOT EXISTS idx_times_keywords ON times USING GIN(keywords);

-- ========================================
-- VIEWS ÚTEIS
-- ========================================

-- View para relatórios de chamados
CREATE OR REPLACE VIEW vw_relatorio_chamados AS
SELECT 
    p.nome as prefeitura,
    t.nome as time,
    cc.nome as categoria,
    c.protocolo,
    c.titulo,
    c.status,
    c.prioridade,
    cid.nome as cidadao,
    cid.telefone,
    c.created_at,
    c.resolved_at,
    CASE 
        WHEN c.resolved_at IS NOT NULL THEN 
            EXTRACT(EPOCH FROM (c.resolved_at - c.created_at))/3600
        ELSE 
            EXTRACT(EPOCH FROM (NOW() - c.created_at))/3600
    END as horas_resolucao,
    CASE 
        WHEN c.resolved_at IS NOT NULL AND c.sla_deadline IS NOT NULL THEN
            CASE WHEN c.resolved_at <= c.sla_deadline THEN 'DENTRO DO SLA' ELSE 'FORA DO SLA' END
        ELSE 'EM ANDAMENTO'
    END as sla_status
FROM chamados c
JOIN prefeituras p ON c.prefeitura_id = p.id
LEFT JOIN times t ON c.time_id = t.id
LEFT JOIN categorias_chamados cc ON c.categoria_id = cc.id
JOIN cidadaos cid ON c.cidadao_id = cid.id;

-- View para dashboard de métricas
CREATE OR REPLACE VIEW vw_dashboard_metrics AS
SELECT 
    p.id as prefeitura_id,
    p.nome as prefeitura,
    COUNT(c.id) as total_chamados,
    COUNT(CASE WHEN c.status = 'aberto' THEN 1 END) as chamados_abertos,
    COUNT(CASE WHEN c.status = 'em_andamento' THEN 1 END) as chamados_andamento,
    COUNT(CASE WHEN c.status = 'resolvido' THEN 1 END) as chamados_resolvidos,
    COUNT(CASE WHEN c.status = 'cancelado' THEN 1 END) as chamados_cancelados,
    AVG(CASE 
        WHEN c.resolved_at IS NOT NULL THEN 
            EXTRACT(EPOCH FROM (c.resolved_at - c.created_at))/3600
        ELSE NULL
    END) as tempo_medio_resolucao_horas
FROM prefeituras p
LEFT JOIN chamados c ON p.id = c.prefeitura_id
WHERE p.active = true
GROUP BY p.id, p.nome;

-- ========================================
-- DADOS INICIAIS
-- ========================================

-- Inserir prefeitura padrão (usar dados reais do Chatwoot)
INSERT INTO prefeituras (nome, chatwoot_account_id, whatsapp_number, config) 
VALUES ('Prefeitura de Teste', 1, '+557798755764', '{"sla_padrao": 72, "timezone": "America/Bahia"}')
ON CONFLICT (chatwoot_account_id) DO NOTHING;

-- Inserir times padrão
INSERT INTO times (prefeitura_id, nome, keywords, cor, config) VALUES
(1, 'Infraestrutura', ARRAY['buraco', 'rua', 'asfalto', 'calçada', 'iluminação', 'esgoto', 'poste', 'pavimentação'], '#FF6B6B', '{"sla_horas": 48, "prioridade_padrao": "normal"}'),
(1, 'Saúde', ARRAY['posto', 'saúde', 'médico', 'remédio', 'hospital', 'clínica', 'atendimento'], '#4ECDC4', '{"sla_horas": 24, "prioridade_padrao": "alta"}'),
(1, 'Educação', ARRAY['escola', 'educação', 'professor', 'merenda', 'transporte', 'ensino'], '#45B7D1', '{"sla_horas": 72, "prioridade_padrao": "normal"}'),
(1, 'Assistência Social', ARRAY['bolsa', 'assistência', 'social', 'cadastro', 'benefício', 'auxílio'], '#96CEB4', '{"sla_horas": 120, "prioridade_padrao": "normal"}'),
(1, 'Obras', ARRAY['obra', 'construção', 'reforma', 'pavimentação', 'construir'], '#FFEAA7', '{"sla_horas": 168, "prioridade_padrao": "normal"}')
ON CONFLICT DO NOTHING;

-- Inserir agente IA padrão
INSERT INTO agentes (prefeitura_id, nome, tipo, config) VALUES
(1, 'Agente IA Geral', 'ia_geral', '{"model": "llama-3.1-8b-instant", "temperature": 0.7, "max_tokens": 300}'),
(1, 'Agente IA Cadastro', 'ia_cadastro', '{"model": "llama-3.1-8b-instant", "temperature": 0.5, "max_tokens": 200}'),
(1, 'Agente IA Infraestrutura', 'ia_infraestrutura', '{"model": "llama-3.1-8b-instant", "temperature": 0.6, "max_tokens": 250}')
ON CONFLICT DO NOTHING;

-- Associar agente IA geral a todos os times
INSERT INTO agente_times (agente_id, time_id, role)
SELECT 1, id, 'admin' FROM times WHERE prefeitura_id = 1
ON CONFLICT (agente_id, time_id) DO NOTHING;

-- Inserir categorias padrão
INSERT INTO categorias_chamados (prefeitura_id, time_id, nome, keywords, sla_horas, prioridade, template_resposta) VALUES
(1, 1, 'Buraco na Rua', ARRAY['buraco', 'rua', 'asfalto', 'buraco na rua'], 24, 'normal', 'Seu chamado sobre buraco na rua foi registrado. Nossa equipe de infraestrutura será notificada.'),
(1, 1, 'Falta de Iluminação', ARRAY['luz', 'iluminação', 'poste', 'escuro', 'lampião'], 48, 'normal', 'Sua solicitação de iluminação foi registrada. Nossa equipe técnica será acionada.'),
(1, 1, 'Esgoto a Céu Aberto', ARRAY['esgoto', 'esgoto a céu aberto', 'vala', 'fossa'], 12, 'alta', 'Urgente! Seu chamado sobre esgoto foi registrado como alta prioridade.'),
(1, 2, 'Posto de Saúde', ARRAY['posto', 'saúde', 'médico', 'atendimento', 'consulta'], 24, 'alta', 'Sua solicitação de saúde foi registrada. Nossa equipe de saúde será contatada.'),
(1, 3, 'Merenda Escolar', ARRAY['merenda', 'escola', 'alimentação', 'lanche'], 168, 'normal', 'Sua solicitação sobre merenda escolar foi registrada.'),
(1, 4, 'Cadastro Único', ARRAY['cadastro', 'cadastro único', 'benefício', 'bolsa'], 120, 'normal', 'Sua solicitação de cadastro foi registrada. Nossa equipe de assistência social entrará em contato.'),
(1, 5, 'Obra Pública', ARRAY['obra', 'construção', 'reforma', 'pavimentação'], 168, 'normal', 'Sua solicitação de obra foi registrada. Nossa equipe de obras será notificada.')
ON CONFLICT DO NOTHING;

-- ========================================
-- FUNÇÕES AUXILIARES
-- ========================================

-- Função para gerar protocolo único
CREATE OR REPLACE FUNCTION gerar_protocolo_chamado(
    p_time_id INT,
    p_ano INT DEFAULT EXTRACT(YEAR FROM NOW())
) RETURNS TEXT AS $$
DECLARE
    v_prefixo TEXT;
    v_sequencial INT;
    v_protocolo TEXT;
BEGIN
    -- Obter prefixo do time
    SELECT UPPER(SUBSTRING(nome, 1, 5)) INTO v_prefixo
    FROM times 
    WHERE id = p_time_id;
    
    -- Obter próximo sequencial
    SELECT COALESCE(MAX(CAST(SUBSTRING(protocolo FROM '\d+$') AS INT)), 0) + 1 INTO v_sequencial
    FROM chamados 
    WHERE protocolo LIKE v_prefixo || '-' || p_ano || '-%';
    
    -- Gerar protocolo
    v_protocolo := v_prefixo || '-' || p_ano || '-' || LPAD(v_sequencial::TEXT, 3, '0');
    
    RETURN v_protocolo;
END;
$$ LANGUAGE plpgsql;

-- Função para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para updated_at
CREATE TRIGGER update_cidadaos_updated_at BEFORE UPDATE ON cidadaos FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_chamados_updated_at BEFORE UPDATE ON chamados FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- COMMIT
-- ========================================

COMMIT;
