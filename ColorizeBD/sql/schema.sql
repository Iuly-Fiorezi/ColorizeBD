CREATE TABLE usuarios (
    id BIGSERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(254) NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    tipo VARCHAR(20) NOT NULL DEFAULT 'usuario'
        -- Só permite os dois tipos de conta usados pelo sistema.
        CHECK (tipo IN ('usuario', 'admin')),
    criado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sessoes (
    id BIGSERIAL PRIMARY KEY,
    usuario_id BIGINT NOT NULL
        -- A sessão precisa pertencer a um usuário existente.
        REFERENCES usuarios(id)
        -- Se o usuário for apagado, suas sessões também são apagadas.
        ON DELETE CASCADE,
    token_hash TEXT NOT NULL UNIQUE,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expira_em TIMESTAMPTZ NOT NULL
);

CREATE TABLE filtros (
    id BIGSERIAL PRIMARY KEY,
    usuario_id BIGINT NOT NULL
        REFERENCES usuarios(id)
        ON DELETE CASCADE,
    nome VARCHAR(100) NOT NULL,
    intensidade_r NUMERIC(3,2) NOT NULL
        CHECK (intensidade_r BETWEEN 0.5 AND 1),
    intensidade_g NUMERIC(3,2) NOT NULL
        CHECK (intensidade_g BETWEEN 0.5 AND 1),
    intensidade_b NUMERIC(3,2) NOT NULL
        CHECK (intensidade_b BETWEEN 0.5 AND 1)
);
