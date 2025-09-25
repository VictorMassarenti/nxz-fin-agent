-- Tabela para registrar negociações com clientes
CREATE TABLE IF NOT EXISTS negociacoes (
    id SERIAL PRIMARY KEY,
    cnpj VARCHAR(18) NOT NULL,
    detalhes TEXT NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice para busca rápida por CNPJ
CREATE INDEX IF NOT EXISTS idx_negociacoes_cnpj ON negociacoes(cnpj);

-- Trigger para atualizar data_atualizacao automaticamente
CREATE OR REPLACE FUNCTION update_data_atualizacao()
RETURNS TRIGGER AS $$
BEGIN
    NEW.data_atualizacao = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_negociacoes_data_atualizacao
    BEFORE UPDATE ON negociacoes
    FOR EACH ROW
    EXECUTE FUNCTION update_data_atualizacao();