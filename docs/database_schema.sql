-- ========================================
-- SISTEMA DE CHAMADOS CIDADÃOS - SCHEMA
-- ========================================

-- 1. PREFEITURAS/CLIENTES (Caixas de Entrada)
CREATE TABLE prefeituras (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL, -- "Prefeitura de São Paulo"
    chatwoot_account_id INT UNIQUE, -- ID da conta no Chatwoot
    chatwoot_inbox_id INT, -- ID da caixa de entrada
    whatsapp_number VARCHAR(20), -- Número do WhatsApp
    config JSONB, -- Configurações específicas
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 2. TIMES/SECRETARIAS
CREATE TABLE times (
    id SERIAL PRIMARY KEY,
    prefeitura_id INT REFERENCES prefeituras(id),
    nome VARCHAR(100) NOT NULL, -- "Infraestrutura", "Saúde", "Educação"
    chatwoot_team_id INT, -- ID do team no Chatwoot
    cor VARCHAR(7), -- Cor para identificação visual
    keywords TEXT[], -- Palavras-chave para IA categorizar
    responsavel_nome VARCHAR(255),
    responsavel_email VARCHAR(255),
    config JSONB, -- Configurações específicas do time
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 3. AGENTES (Humanos e IA)
CREATE TABLE agentes (
    id SERIAL PRIMARY KEY,
    prefeitura_id INT REFERENCES prefeituras(id),
    nome VARCHAR(255) NOT NULL,
    tipo VARCHAR(20) NOT NULL, -- "humano", "ia_cadastro", "ia_infraestrutura", "ia_geral"
    chatwoot_agent_id INT, -- ID do agente no Chatwoot (NULL para IA)
    email VARCHAR(255),
    telefone VARCHAR(20),
    config JSONB, -- Configurações específicas do agente
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 4. RELACIONAMENTO AGENTE-TIME
CREATE TABLE agente_times (
    id SERIAL PRIMARY KEY,
    agente_id INT REFERENCES agentes(id),
    time_id INT REFERENCES times(id),
    role VARCHAR(50) DEFAULT 'member', -- "member", "admin"
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(agente_id, time_id)
);

-- 5. CIDADÃOS
CREATE TABLE cidadaos (
    id SERIAL PRIMARY KEY,
    prefeitura_id INT REFERENCES prefeituras(id),
    nome VARCHAR(255) NOT NULL,
    cpf VARCHAR(14) UNIQUE,
    telefone VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    endereco TEXT,
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    cep VARCHAR(10),
    chatwoot_contact_id INT, -- ID do contato no Chatwoot
    data_nascimento DATE,
    genero VARCHAR(20),
    config JSONB, -- Dados adicionais
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 6. CATEGORIAS DE CHAMADOS
CREATE TABLE categorias_chamados (
    id SERIAL PRIMARY KEY,
    prefeitura_id INT REFERENCES prefeituras(id),
    time_id INT REFERENCES times(id),
    nome VARCHAR(100) NOT NULL, -- "Buraco na Rua", "Falta de Energia"
    descricao TEXT,
    keywords TEXT[], -- Palavras-chave para IA
    prioridade VARCHAR(20) DEFAULT 'normal', -- "baixa", "normal", "alta", "urgente"
    sla_horas INT DEFAULT 72, -- SLA em horas
    template_resposta TEXT, -- Template de resposta automática
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 7. CHAMADOS/PROTOCOLOS
CREATE TABLE chamados (
    id SERIAL PRIMARY KEY,
    prefeitura_id INT REFERENCES prefeituras(id),
    protocolo VARCHAR(50) UNIQUE NOT NULL, -- "INFRA-2024-001"
    cidadao_id INT REFERENCES cidadaos(id),
    categoria_id INT REFERENCES categorias_chamados(id),
    time_id INT REFERENCES times(id),
    chatwoot_conversation_id INT, -- ID da conversa no Chatwoot
    
    -- Dados do chamado
    titulo VARCHAR(255) NOT NULL,
    descricao TEXT NOT NULL,
    endereco_ocorrencia TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    
    -- Status e fluxo
    status VARCHAR(50) DEFAULT 'aberto', -- "aberto", "em_andamento", "resolvido", "cancelado"
    prioridade VARCHAR(20) DEFAULT 'normal',
    sla_deadline TIMESTAMP,
    
    -- Atribuições
    agente_responsavel_id INT REFERENCES agentes(id),
    agente_atribuido_por_id INT REFERENCES agentes(id),
    
    -- Metadados
    fonte VARCHAR(50) DEFAULT 'whatsapp', -- "whatsapp", "web", "telefone"
    tags TEXT[], -- Tags adicionais
    anexos JSONB, -- URLs dos anexos
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP,
    
    -- Configurações
    config JSONB
);

-- 8. INTERAÇÕES/HISTÓRICO
CREATE TABLE interacoes_chamado (
    id SERIAL PRIMARY KEY,
    chamado_id INT REFERENCES chamados(id),
    agente_id INT REFERENCES agentes(id),
    tipo VARCHAR(50) NOT NULL, -- "mensagem", "atribuicao", "status_change", "comentario"
    conteudo TEXT,
    metadata JSONB, -- Dados específicos do tipo de interação
    created_at TIMESTAMP DEFAULT NOW()
);

-- 9. TEMPLATES DE RESPOSTA
CREATE TABLE templates_resposta (
    id SERIAL PRIMARY KEY,
    prefeitura_id INT REFERENCES prefeituras(id),
    categoria_id INT REFERENCES categorias_chamados(id),
    nome VARCHAR(100) NOT NULL,
    template TEXT NOT NULL,
    variaveis JSONB, -- Variáveis disponíveis no template
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 10. CONFIGURAÇÕES DE IA
CREATE TABLE config_ia (
    id SERIAL PRIMARY KEY,
    prefeitura_id INT REFERENCES prefeituras(id),
    agente_id INT REFERENCES agentes(id),
    nome VARCHAR(100) NOT NULL, -- "cadastro", "categorizacao", "atendimento"
    prompt_system TEXT,
    config JSONB, -- Configurações específicas
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ========================================
-- ÍNDICES PARA PERFORMANCE
-- ========================================

CREATE INDEX idx_cidadaos_telefone ON cidadaos(telefone);
CREATE INDEX idx_cidadaos_cpf ON cidadaos(cpf);
CREATE INDEX idx_cidadaos_prefeitura ON cidadaos(prefeitura_id);

CREATE INDEX idx_chamados_protocolo ON chamados(protocolo);
CREATE INDEX idx_chamados_cidadao ON chamados(cidadao_id);
CREATE INDEX idx_chamados_status ON chamados(status);
CREATE INDEX idx_chamados_prefeitura ON chamados(prefeitura_id);
CREATE INDEX idx_chamados_time ON chamados(time_id);
CREATE INDEX idx_chamados_created ON chamados(created_at);

CREATE INDEX idx_interacoes_chamado ON interacoes_chamado(chamado_id);
CREATE INDEX idx_interacoes_created ON interacoes_chamado(created_at);

-- ========================================
-- VIEWS ÚTEIS
-- ========================================

-- View para relatórios de chamados
CREATE VIEW vw_relatorio_chamados AS
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
    END as horas_resolucao
FROM chamados c
JOIN prefeituras p ON c.prefeitura_id = p.id
JOIN times t ON c.time_id = t.id
JOIN categorias_chamados cc ON c.categoria_id = cc.id
JOIN cidadaos cid ON c.cidadao_id = cid.id;

-- ========================================
-- DADOS INICIAIS
-- ========================================

-- Inserir prefeitura padrão
INSERT INTO prefeituras (nome, chatwoot_account_id, whatsapp_number) 
VALUES ('Prefeitura de Teste', 1, '+557798755764');

-- Inserir times padrão
INSERT INTO times (prefeitura_id, nome, keywords, cor) VALUES
(1, 'Infraestrutura', ARRAY['buraco', 'rua', 'asfalto', 'calçada', 'iluminação', 'esgoto'], '#FF6B6B'),
(1, 'Saúde', ARRAY['posto', 'saúde', 'médico', 'remédio', 'hospital'], '#4ECDC4'),
(1, 'Educação', ARRAY['escola', 'educação', 'professor', 'merenda', 'transporte'], '#45B7D1'),
(1, 'Assistência Social', ARRAY['bolsa', 'assistência', 'social', 'cadastro', 'benefício'], '#96CEB4'),
(1, 'Obras', ARRAY['obra', 'construção', 'reforma', 'pavimentação'], '#FFEAA7');

-- Inserir agente IA padrão
INSERT INTO agentes (prefeitura_id, nome, tipo, config) VALUES
(1, 'Agente IA Geral', 'ia_geral', '{"model": "llama-3.1-8b-instant", "temperature": 0.7}'),
(1, 'Agente IA Cadastro', 'ia_cadastro', '{"model": "llama-3.1-8b-instant", "temperature": 0.5}'),
(1, 'Agente IA Infraestrutura', 'ia_infraestrutura', '{"model": "llama-3.1-8b-instant", "temperature": 0.6}');

-- Associar agente IA a todos os times
INSERT INTO agente_times (agente_id, time_id, role)
SELECT 1, id, 'admin' FROM times WHERE prefeitura_id = 1;

-- Inserir categorias padrão
INSERT INTO categorias_chamados (prefeitura_id, time_id, nome, keywords, sla_horas) VALUES
(1, 1, 'Buraco na Rua', ARRAY['buraco', 'rua', 'asfalto', 'buraco na rua'], 24),
(1, 1, 'Falta de Iluminação', ARRAY['luz', 'iluminação', 'poste', 'escuro'], 48),
(1, 1, 'Esgoto', ARRAY['esgoto', 'esgoto a céu aberto', 'vala'], 12),
(1, 2, 'Posto de Saúde', ARRAY['posto', 'saúde', 'médico', 'atendimento'], 72),
(1, 3, 'Merenda Escolar', ARRAY['merenda', 'escola', 'alimentação'], 168);
