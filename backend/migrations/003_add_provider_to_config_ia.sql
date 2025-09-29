-- Migration para adicionar coluna provider na tabela config_ia
-- Data: 29 de Dezembro de 2024

-- Adicionar coluna provider na tabela config_ia
ALTER TABLE config_ia ADD COLUMN IF NOT EXISTS provider VARCHAR(50) DEFAULT 'groq';

-- Atualizar registros existentes
UPDATE config_ia SET provider = 'groq' WHERE provider IS NULL;

-- Adicionar índice para performance
CREATE INDEX IF NOT EXISTS idx_config_ia_provider ON config_ia(provider);

-- Comentário na coluna
COMMENT ON COLUMN config_ia.provider IS 'Provedor de IA: groq, openai, anthropic';
