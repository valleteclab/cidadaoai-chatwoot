-- Migration para adicionar tabela de interações dos agentes
-- Data: 29 de Dezembro de 2024

-- Tabela para armazenar interações dos agentes IA
CREATE TABLE IF NOT EXISTS agent_interactions (
    id SERIAL PRIMARY KEY,
    agent_id INTEGER NOT NULL REFERENCES config_ia(id) ON DELETE CASCADE,
    user_message TEXT NOT NULL,
    ai_response TEXT,
    response_time DECIMAL(10,3), -- tempo em segundos
    tokens_used INTEGER DEFAULT 0,
    
    cost DECIMAL(10,6) DEFAULT 0.0,
    success BOOLEAN DEFAULT true,
    category VARCHAR(100),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_agent_interactions_agent_id ON agent_interactions(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_interactions_created_at ON agent_interactions(created_at);
CREATE INDEX IF NOT EXISTS idx_agent_interactions_success ON agent_interactions(success);
CREATE INDEX IF NOT EXISTS idx_agent_interactions_category ON agent_interactions(category);

-- Função para registrar interação do agente
CREATE OR REPLACE FUNCTION register_agent_interaction(
    p_agent_id INTEGER,
    p_user_message TEXT,
    p_ai_response TEXT,
    p_response_time DECIMAL(10,3),
    p_tokens_used INTEGER DEFAULT 0,
    p_cost DECIMAL(10,6) DEFAULT 0.0,
    p_success BOOLEAN DEFAULT true,
    p_category VARCHAR(100) DEFAULT NULL,
    p_metadata JSONB DEFAULT NULL
) RETURNS INTEGER AS $$
DECLARE
    interaction_id INTEGER;
BEGIN
    INSERT INTO agent_interactions (
        agent_id, user_message, ai_response, response_time,
        tokens_used, cost, success, category, metadata
    ) VALUES (
        p_agent_id, p_user_message, p_ai_response, p_response_time,
        p_tokens_used, p_cost, p_success, p_category, p_metadata
    ) RETURNING id INTO interaction_id;
    
    RETURN interaction_id;
END;
$$ LANGUAGE plpgsql;

-- View para analytics de agentes
CREATE OR REPLACE VIEW vw_agent_analytics AS
SELECT 
    ai.id as agent_id,
    ai.nome as agent_name,
    (ai.config->>'provider')::text as provider,
    COUNT(inter.id) as total_interactions,
    AVG(inter.response_time) as avg_response_time,
    MIN(inter.response_time) as min_response_time,
    MAX(inter.response_time) as max_response_time,
    COUNT(CASE WHEN inter.success = true THEN 1 END) as successful_interactions,
    COUNT(CASE WHEN inter.success = false THEN 1 END) as failed_interactions,
    ROUND(
        (COUNT(CASE WHEN inter.success = true THEN 1 END)::DECIMAL / COUNT(inter.id)) * 100, 2
    ) as success_rate,
    SUM(inter.tokens_used) as total_tokens,
    AVG(inter.tokens_used) as avg_tokens_per_interaction,
    SUM(inter.cost) as total_cost,
    AVG(inter.cost) as avg_cost_per_interaction,
    MAX(inter.created_at) as last_interaction
FROM config_ia ai
LEFT JOIN agent_interactions inter ON ai.id = inter.agent_id
GROUP BY ai.id, ai.nome, (ai.config->>'provider')::text;

-- View para performance por hora
CREATE OR REPLACE VIEW vw_agent_hourly_performance AS
SELECT 
    ai.id as agent_id,
    ai.nome as agent_name,
    EXTRACT(HOUR FROM inter.created_at) as hour,
    COUNT(inter.id) as interactions,
    AVG(inter.response_time) as avg_response_time,
    COUNT(CASE WHEN inter.success = true THEN 1 END) as successful,
    COUNT(CASE WHEN inter.success = false THEN 1 END) as failed
FROM config_ia ai
LEFT JOIN agent_interactions inter ON ai.id = inter.agent_id
GROUP BY ai.id, ai.nome, EXTRACT(HOUR FROM inter.created_at)
ORDER BY ai.id, hour;

-- View para top queries por agente
CREATE OR REPLACE VIEW vw_agent_top_queries AS
SELECT 
    ai.id as agent_id,
    ai.nome as agent_name,
    inter.user_message,
    COUNT(*) as frequency,
    AVG(inter.response_time) as avg_response_time,
    COUNT(CASE WHEN inter.success = true THEN 1 END) as successful,
    COUNT(CASE WHEN inter.success = false THEN 1 END) as failed
FROM config_ia ai
LEFT JOIN agent_interactions inter ON ai.id = inter.agent_id
WHERE inter.user_message IS NOT NULL
GROUP BY ai.id, ai.nome, inter.user_message
ORDER BY ai.id, frequency DESC;

-- Comentários
COMMENT ON TABLE agent_interactions IS 'Armazena interações dos agentes IA para analytics';
COMMENT ON COLUMN agent_interactions.response_time IS 'Tempo de resposta em segundos';
COMMENT ON COLUMN agent_interactions.tokens_used IS 'Número de tokens utilizados';
COMMENT ON COLUMN agent_interactions.cost IS 'Custo da interação em USD';
COMMENT ON COLUMN agent_interactions.success IS 'Se a interação foi bem-sucedida';
COMMENT ON COLUMN agent_interactions.category IS 'Categoria da interação';
COMMENT ON COLUMN agent_interactions.metadata IS 'Metadados adicionais em JSON';

COMMENT ON VIEW vw_agent_analytics IS 'Analytics consolidados por agente';
COMMENT ON VIEW vw_agent_hourly_performance IS 'Performance dos agentes por hora do dia';
COMMENT ON VIEW vw_agent_top_queries IS 'Top queries mais frequentes por agente';
