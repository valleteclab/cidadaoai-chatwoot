CREATE TABLE IF NOT EXISTS cidadao_enderecos (
    id SERIAL PRIMARY KEY,
    cidadao_id INT NOT NULL REFERENCES cidadaos(id) ON DELETE CASCADE,
    cep VARCHAR(10),
    logradouro VARCHAR(255),
    numero VARCHAR(20),
    bairro VARCHAR(120),
    cidade VARCHAR(120),
    estado VARCHAR(2),
    complemento VARCHAR(255),
    is_principal BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cidadao_enderecos_cidadao ON cidadao_enderecos(cidadao_id);

ALTER TABLE cidadaos
    DROP COLUMN IF EXISTS endereco,
    DROP COLUMN IF EXISTS bairro,
    DROP COLUMN IF EXISTS cidade,
    DROP COLUMN IF EXISTS cep,
    ADD COLUMN IF NOT EXISTS numero VARCHAR(20),
    ADD COLUMN IF NOT EXISTS estado VARCHAR(2),
    ADD COLUMN IF NOT EXISTS complemento VARCHAR(255);

CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS set_timestamp_cidadao_enderecos ON cidadao_enderecos;
CREATE TRIGGER set_timestamp_cidadao_enderecos
BEFORE UPDATE ON cidadao_enderecos
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();
