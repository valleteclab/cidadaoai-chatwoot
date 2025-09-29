-- Migration para adicionar coluna updated_at na tabela config_ia
-- Data: 29 de Dezembro de 2024

-- Adicionar coluna updated_at na tabela config_ia
ALTER TABLE config_ia ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();

-- Criar função para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_config_ia_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Criar trigger para atualizar updated_at automaticamente
DROP TRIGGER IF EXISTS trigger_update_config_ia_updated_at ON config_ia;
CREATE TRIGGER trigger_update_config_ia_updated_at
    BEFORE UPDATE ON config_ia
    FOR EACH ROW
    EXECUTE FUNCTION update_config_ia_updated_at();

-- Atualizar registros existentes
UPDATE config_ia SET updated_at = NOW() WHERE updated_at IS NULL;

-- Comentário na coluna
COMMENT ON COLUMN config_ia.updated_at IS 'Timestamp de última atualização do registro';
