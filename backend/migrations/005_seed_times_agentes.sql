-- 005_seed_times_agentes.sql
-- Seed inicial de Times, Agentes e vínculos agente_times (idempotente)

BEGIN;

-- ======================
-- TIMES (insere se não existir)
-- ======================
INSERT INTO times (prefeitura_id, nome, chatwoot_team_id, cor, keywords, responsavel_nome, responsavel_email, config, active, created_at)
SELECT 1, 'Obras', NULL, '#F6E05E', ARRAY['obras','pavimentação','asfalto','calçada','buraco'], NULL, NULL, '{}'::jsonb, TRUE, NOW()
WHERE NOT EXISTS (SELECT 1 FROM times WHERE prefeitura_id=1 AND nome='Obras');

INSERT INTO times (prefeitura_id, nome, chatwoot_team_id, cor, keywords, responsavel_nome, responsavel_email, config, active, created_at)
SELECT 1, 'Infraestrutura', NULL, '#F56565', ARRAY['iluminação','poste','rede elétrica','água','esgoto','bueiro'], NULL, NULL, '{}'::jsonb, TRUE, NOW()
WHERE NOT EXISTS (SELECT 1 FROM times WHERE prefeitura_id=1 AND nome='Infraestrutura');

INSERT INTO times (prefeitura_id, nome, chatwoot_team_id, cor, keywords, responsavel_nome, responsavel_email, config, active, created_at)
SELECT 1, 'Saúde', NULL, '#4FD1C5', ARRAY['saúde','posto','vacina','medicamento','agendamento'], NULL, NULL, '{}'::jsonb, TRUE, NOW()
WHERE NOT EXISTS (SELECT 1 FROM times WHERE prefeitura_id=1 AND nome='Saúde');

INSERT INTO times (prefeitura_id, nome, chatwoot_team_id, cor, keywords, responsavel_nome, responsavel_email, config, active, created_at)
SELECT 1, 'Educação', NULL, '#63B3ED', ARRAY['escola','matrícula','merenda','professor','transporte escolar'], NULL, NULL, '{}'::jsonb, TRUE, NOW()
WHERE NOT EXISTS (SELECT 1 FROM times WHERE prefeitura_id=1 AND nome='Educação');

INSERT INTO times (prefeitura_id, nome, chatwoot_team_id, cor, keywords, responsavel_nome, responsavel_email, config, active, created_at)
SELECT 1, 'Assistência Social', NULL, '#9AE6B4', ARRAY['assistência','bolsa','cadastro único','CRAS','CREAS'], NULL, NULL, '{}'::jsonb, TRUE, NOW()
WHERE NOT EXISTS (SELECT 1 FROM times WHERE prefeitura_id=1 AND nome='Assistência Social');

-- ======================
-- AGENTES (insere se não existir)
-- ======================
INSERT INTO agentes (prefeitura_id, nome, tipo, chatwoot_agent_id, email, telefone, config, active, created_at)
SELECT 1, 'Agente IA Geral', 'ia_geral', NULL, NULL, NULL, '{}'::jsonb, TRUE, NOW()
WHERE NOT EXISTS (SELECT 1 FROM agentes WHERE prefeitura_id=1 AND nome='Agente IA Geral');

INSERT INTO agentes (prefeitura_id, nome, tipo, chatwoot_agent_id, email, telefone, config, active, created_at)
SELECT 1, 'Agente IA Cadastro', 'ia_cadastro', NULL, NULL, NULL, '{}'::jsonb, TRUE, NOW()
WHERE NOT EXISTS (SELECT 1 FROM agentes WHERE prefeitura_id=1 AND nome='Agente IA Cadastro');

INSERT INTO agentes (prefeitura_id, nome, tipo, chatwoot_agent_id, email, telefone, config, active, created_at)
SELECT 1, 'Agente IA Infraestrutura', 'ia_infraestrutura', NULL, NULL, NULL, '{}'::jsonb, TRUE, NOW()
WHERE NOT EXISTS (SELECT 1 FROM agentes WHERE prefeitura_id=1 AND nome='Agente IA Infraestrutura');

-- ======================
-- VÍNCULOS agente_times (não duplica)
-- ======================
-- Agente IA Geral -> todos os times
INSERT INTO agente_times (agente_id, time_id, created_at)
SELECT a.id, t.id, NOW()
FROM agentes a
JOIN times t ON t.prefeitura_id=1
WHERE a.prefeitura_id=1 AND a.nome='Agente IA Geral'
  AND NOT EXISTS (
    SELECT 1 FROM agente_times at WHERE at.agente_id=a.id AND at.time_id=t.id
  );

-- Agente IA Cadastro -> Educação, Assistência Social, Saúde
INSERT INTO agente_times (agente_id, time_id, created_at)
SELECT a.id, t.id, NOW()
FROM agentes a
JOIN times t ON t.prefeitura_id=1 AND t.nome IN ('Educação','Assistência Social','Saúde')
WHERE a.prefeitura_id=1 AND a.nome='Agente IA Cadastro'
  AND NOT EXISTS (
    SELECT 1 FROM agente_times at WHERE at.agente_id=a.id AND at.time_id=t.id
  );

-- Agente IA Infraestrutura -> Infraestrutura, Obras
INSERT INTO agente_times (agente_id, time_id, created_at)
SELECT a.id, t.id, NOW()
FROM agentes a
JOIN times t ON t.prefeitura_id=1 AND t.nome IN ('Infraestrutura','Obras')
WHERE a.prefeitura_id=1 AND a.nome='Agente IA Infraestrutura'
  AND NOT EXISTS (
    SELECT 1 FROM agente_times at WHERE at.agente_id=a.id AND at.time_id=t.id
  );

COMMIT;

-- Conferência (opcional)
-- SELECT a.id, a.nome, STRING_AGG(DISTINCT t.nome, ', ') AS times
-- FROM agentes a
-- LEFT JOIN agente_times at ON at.agente_id=a.id
-- LEFT JOIN times t ON t.id=at.time_id
-- WHERE a.prefeitura_id=1
-- GROUP BY a.id, a.nome
-- ORDER BY a.id DESC;


