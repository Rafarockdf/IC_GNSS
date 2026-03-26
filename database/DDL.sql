-- Criação da tabela de Estações
CREATE TABLE IF NOT EXISTS estacoes (
    id_municipio  TEXT,
    id_estacao    TEXT PRIMARY KEY,
    estacao       TEXT,
    data_fundacao DATE,
    latitude      REAL,
    longitude     REAL,
    altitude      REAL
);

-- Criação da tabela de Microdados
CREATE TABLE IF NOT EXISTS microdados (
    id_microdados          INTEGER PRIMARY KEY AUTOINCREMENT,
    ano                     INTEGER,
    mes                     INTEGER,
    data                    DATE,
    hora                    TEXT,
    id_estacao              TEXT,
    precipitacao_total      REAL,
    pressao_atm_hora        REAL,
    pressao_atm_max         REAL,
    pressao_atm_min         REAL,
    radiacao_global         REAL,
    temperatura_bulbo_hora  REAL,
    temperatura_orvalho_hora REAL,
    temperatura_max         REAL,
    temperatura_min         REAL,
    temperatura_orvalho_max  REAL,
    temperatura_orvalho_min  REAL,
    umidade_rel_max         REAL,
    umidade_rel_min         REAL,
    umidade_rel_hora        REAL,
    vento_direcao           REAL,
    vento_rajada_max        REAL,
    vento_velocidade        REAL,
    FOREIGN KEY (id_estacao) REFERENCES estacoes (id_estacao)
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_microdados_data ON microdados (data);
CREATE INDEX IF NOT EXISTS idx_microdados_estacao ON microdados (id_estacao);