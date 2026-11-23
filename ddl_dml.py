from conexao import conectar

DDL_SCRIPT = """
CREATE DATABASE IF NOT EXISTS sgfi CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE sgfi;

CREATE TABLE IF NOT EXISTS estabelecimento (
    id_estabelec INT NOT NULL AUTO_INCREMENT,
    cnpj VARCHAR(18) NOT NULL UNIQUE,
    nome VARCHAR(120) NOT NULL,
    endereco VARCHAR(200),
    telefone VARCHAR(20),
    PRIMARY KEY (id_estabelec)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS unidade (
    id_unidade INT NOT NULL AUTO_INCREMENT,
    nome_unid VARCHAR(120) NOT NULL,
    telefone VARCHAR(20),
    enderc VARCHAR(200),
    status_unidade VARCHAR(10) NOT NULL DEFAULT 'ATIVA',
    id_estabelec INT NOT NULL,
    PRIMARY KEY (id_unidade),
    CHECK (status_unidade IN ('ATIVA', 'INATIVA')),
    FOREIGN KEY (id_estabelec) REFERENCES estabelecimento (id_estabelec) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS horar_funcionamento (
    id_hora_func INT NOT NULL AUTO_INCREMENT,
    dia_semana SMALLINT NOT NULL,
    hr_abertur TIME NOT NULL,
    hr_fechamento TIME NOT NULL,
    status_func VARCHAR(10) NOT NULL DEFAULT 'ABERTO',
    id_unidade INT NOT NULL,
    PRIMARY KEY (id_hora_func),
    UNIQUE (id_unidade, dia_semana),
    CHECK (dia_semana BETWEEN 0 AND 6),
    CHECK (hr_fechamento > hr_abertur),
    CHECK (status_func IN ('ABERTO', 'FECHADO')),
    FOREIGN KEY (id_unidade) REFERENCES unidade (id_unidade) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS administrador (
    id_admin INT NOT NULL AUTO_INCREMENT,
    nome VARCHAR(120) NOT NULL,
    senha VARCHAR(255) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    PRIMARY KEY (id_admin)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS configuracao (
    id_config INT NOT NULL AUTO_INCREMENT,
    tempo_toleranc INT NOT NULL DEFAULT 5,
    media_atend INT NOT NULL DEFAULT 20,
    prioridade_idoso BOOLEAN NOT NULL DEFAULT TRUE,
    data_atualiza DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_admin INT NOT NULL,
    id_unidade INT NOT NULL,
    PRIMARY KEY (id_config),
    CHECK (tempo_toleranc >= 0),
    CHECK (media_atend > 0),
    FOREIGN KEY (id_admin) REFERENCES administrador (id_admin) ON DELETE CASCADE,
    FOREIGN KEY (id_unidade) REFERENCES unidade (id_unidade) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS relatorio (
    id_relat INT NOT NULL AUTO_INCREMENT,
    data_geracao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    periodo_inicial DATE,
    periodo_final DATE,
    tipo_relatorio VARCHAR(40) NOT NULL,
    id_admin INT NOT NULL,
    PRIMARY KEY (id_relat),
    CHECK (periodo_final IS NULL OR periodo_inicial IS NULL OR periodo_final >= periodo_inicial),
    FOREIGN KEY (id_admin) REFERENCES administrador (id_admin) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS servico (
    id_servico INT NOT NULL AUTO_INCREMENT,
    nome_servic VARCHAR(120) NOT NULL,
    tempo_medio_atend INT NOT NULL,
    descricao VARCHAR(300),
    status_servic VARCHAR(10) NOT NULL DEFAULT 'ATIVO',
    PRIMARY KEY (id_servico),
    CHECK (tempo_medio_atend > 0),
    CHECK (status_servic IN ('ATIVO', 'INATIVO'))
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS fila (
    id_fila INT NOT NULL AUTO_INCREMENT,
    num_fila INT NOT NULL,
    data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status_fila VARCHAR(10) NOT NULL DEFAULT 'ABERTA',
    tempo_medio INT,
    PRIMARY KEY (id_fila),
    CHECK (status_fila IN ('ABERTA', 'FECHADA', 'PAUSADA')),
    CHECK (tempo_medio IS NULL OR tempo_medio >= 0)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS unidade_servico (
    id_unidade INT NOT NULL,
    id_servico INT NOT NULL,
    PRIMARY KEY (id_unidade, id_servico),
    FOREIGN KEY (id_unidade) REFERENCES unidade (id_unidade) ON DELETE CASCADE,
    FOREIGN KEY (id_servico) REFERENCES servico (id_servico) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS servico_fila (
    id_servico INT NOT NULL,
    id_fila INT NOT NULL,
    PRIMARY KEY (id_servico, id_fila),
    FOREIGN KEY (id_servico) REFERENCES servico (id_servico) ON DELETE CASCADE,
    FOREIGN KEY (id_fila) REFERENCES fila (id_fila) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS cliente (
    id_cliente INT NOT NULL AUTO_INCREMENT,
    nome VARCHAR(120) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    senha_aces VARCHAR(255) NOT NULL,
    PRIMARY KEY (id_cliente)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS atendente (
    id_atendente INT NOT NULL AUTO_INCREMENT,
    nome VARCHAR(120) NOT NULL,
    status_atendimento VARCHAR(15) NOT NULL DEFAULT 'INDISPONIVEL',
    senha VARCHAR(255) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    PRIMARY KEY (id_atendente),
    CHECK (status_atendimento IN ('DISPONIVEL', 'INDISPONIVEL', 'EM_ATENDIMENTO'))
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS guiche (
    id_guiche INT NOT NULL AUTO_INCREMENT,
    num_guich INT NOT NULL UNIQUE,
    status_guic VARCHAR(10) NOT NULL DEFAULT 'LIVRE',
    PRIMARY KEY (id_guiche),
    CHECK (status_guic IN ('LIVRE', 'OCUPADO', 'INATIVO'))
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS notificacao (
    id_notifig INT NOT NULL AUTO_INCREMENT,
    tipo_not VARCHAR(10) NOT NULL,
    data_envio DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(10) NOT NULL DEFAULT 'PENDENTE',
    id_cliente INT NOT NULL,
    PRIMARY KEY (id_notifig),
    CHECK (tipo_not IN ('SMS', 'EMAIL', 'PUSH')),
    CHECK (status IN ('PENDENTE', 'ENVIADA', 'FALHOU')),
    FOREIGN KEY (id_cliente) REFERENCES cliente (id_cliente) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS entra_fila (
    id_entrad_fila INT NOT NULL AUTO_INCREMENT,
    numer_senha VARCHAR(10) NOT NULL,
    data_hr_entrad DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    posicao INT,
    data_hr_saida DATETIME,
    tempo_estimad INT,
    id_cliente INT NOT NULL,
    id_fila INT NOT NULL,
    PRIMARY KEY (id_entrad_fila),
    CHECK (posicao IS NULL OR posicao > 0),
    CHECK (tempo_estimad IS NULL OR tempo_estimad >= 0),
    CHECK (data_hr_saida IS NULL OR data_hr_saida >= data_hr_entrad),
    INDEX idx_entra_fila_fila (id_fila),
    INDEX idx_entra_fila_entrada (data_hr_entrad),
    FOREIGN KEY (id_cliente) REFERENCES cliente (id_cliente),
    FOREIGN KEY (id_fila) REFERENCES fila (id_fila)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS atendimento (
    id_atendimento INT NOT NULL AUTO_INCREMENT,
    hr_inicio DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    hr_fim DATETIME,
    status_atendimento VARCHAR(15) NOT NULL DEFAULT 'EM_ANDAMENTO',
    id_entrad_fila INT NOT NULL UNIQUE,
    id_guiche INT NOT NULL,
    id_atendente INT NOT NULL,
    PRIMARY KEY (id_atendimento),
    CHECK (status_atendimento IN ('EM_ANDAMENTO', 'CONCLUIDO', 'AUSENTE')),
    CHECK (hr_fim IS NULL OR hr_fim >= hr_inicio),
    INDEX idx_atendimento_atendente (id_atendente),
    INDEX idx_atendimento_inicio (hr_inicio),
    FOREIGN KEY (id_entrad_fila) REFERENCES entra_fila (id_entrad_fila),
    FOREIGN KEY (id_guiche) REFERENCES guiche (id_guiche),
    FOREIGN KEY (id_atendente) REFERENCES atendente (id_atendente)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS avaliacao (
    id_avaliacao INT NOT NULL AUTO_INCREMENT,
    nota SMALLINT NOT NULL,
    comentario VARCHAR(500),
    data DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_atendimento INT NOT NULL UNIQUE,
    PRIMARY KEY (id_avaliacao),
    CHECK (nota BETWEEN 1 AND 5),
    FOREIGN KEY (id_atendimento) REFERENCES atendimento (id_atendimento) ON DELETE CASCADE
) ENGINE=InnoDB;
"""

DML_SCRIPT = """
USE sgfi;
INSERT IGNORE INTO estabelecimento (id_estabelec, cnpj, nome, endereco, telefone) VALUES (1, '12.345.678/0001-99', 'Rede Atendimento Inteligente', 'Av. Sete de Setembro, 100', '(48) 3522-0000');
INSERT IGNORE INTO unidade (id_unidade, nome_unid, telefone, enderc, status_unidade, id_estabelec) VALUES
(1, 'Unidade Centro', '(48) 3522-1111', 'Rua Coronel Joao Fernandes, 50', 'ATIVA', 1),
(2, 'Unidade Norte',  '(48) 3522-2222', 'Av. Getulio Vargas, 320',        'ATIVA', 1),
(3, 'Unidade Sul',    '(48) 3522-3333', 'Rua Caetano Lummertz, 88',       'ATIVA', 1);
INSERT IGNORE INTO administrador (id_admin, nome, senha, email) VALUES (1, 'Carlos Admin', 'hash_admin_123', 'admin@sgfi.com');
INSERT IGNORE INTO configuracao (id_config, tempo_toleranc, media_atend, prioridade_idoso, id_admin, id_unidade) VALUES (1, 5, 15, TRUE, 1, 1);
INSERT IGNORE INTO horar_funcionamento (id_hora_func, dia_semana, hr_abertur, hr_fechamento, status_func, id_unidade) VALUES (1, 1, '08:00:00', '18:00:00', 'ABERTO', 1);
INSERT IGNORE INTO relatorio (id_relat, periodo_inicial, periodo_final, tipo_relatorio, id_admin) VALUES (1, '2026-11-01', '2026-11-20', 'GERAL', 1);
INSERT IGNORE INTO servico (id_servico, nome_servic, tempo_medio_atend, descricao, status_servic) VALUES
(1, 'Consulta Clinica Geral', 20, 'Atendimento medico clinico', 'ATIVO'),
(2, 'Atendimento Bancario Caixa', 15, 'Pagamentos e saques', 'ATIVO'),
(3, 'Emissao de Documentos', 12, 'Segunda via de documentos', 'ATIVO');
INSERT IGNORE INTO fila (id_fila, num_fila, status_fila, tempo_medio) VALUES (1, 101, 'ABERTA', 20), (2, 102, 'ABERTA', 15), (3, 103, 'ABERTA', 12);
INSERT IGNORE INTO unidade_servico VALUES (1, 1), (2, 2), (3, 3);
INSERT IGNORE INTO servico_fila VALUES (1, 1), (2, 2), (3, 3);
INSERT IGNORE INTO cliente (id_cliente, nome, email, senha_aces) VALUES
(1, 'Pedro Alves', 'pedro@email.com', 'hash_123'),
(2, 'Lucia Mendes', 'lucia@email.com', 'hash_456'),
(3, 'Marcos Lima', 'marcos@email.com', 'hash_789'),
(4, 'Fernanda Dias', 'fernanda@email.com', 'hash_321'),
(5, 'Rafael Costa', 'rafael@email.com', 'hash_654'),
(6, 'Juliana Rocha', 'juliana@email.com', 'hash_987');
INSERT IGNORE INTO atendente (id_atendente, nome, status_atendimento, senha, email) VALUES
(1, 'Maria Silva', 'DISPONIVEL', 'hash_at1', 'maria@sgfi.com'),
(2, 'Joao Souza', 'DISPONIVEL', 'hash_at2', 'joao@sgfi.com'),
(3, 'Ana Costa', 'DISPONIVEL', 'hash_at3', 'ana@sgfi.com');
INSERT IGNORE INTO guiche (id_guiche, num_guich, status_guic) VALUES (1, 1, 'LIVRE'), (2, 2, 'LIVRE'), (3, 3, 'LIVRE');
INSERT IGNORE INTO notificacao (id_notifig, tipo_not, status, id_cliente) VALUES (1, 'EMAIL', 'ENVIADA', 1);
INSERT IGNORE INTO entra_fila (id_entrad_fila, numer_senha, data_hr_entrad, posicao, data_hr_saida, tempo_estimad, id_cliente, id_fila) VALUES
(1, 'A001', '2026-11-10 08:30:00', 1, '2026-11-10 08:55:00', 25, 1, 1),
(2, 'A002', '2026-11-10 08:40:00', 2, '2026-11-10 09:02:00', 22, 2, 1),
(3, 'A003', '2026-11-10 09:00:00', 3, '2026-11-10 09:26:00', 26, 3, 1),
(4, 'B001', '2026-11-10 09:10:00', 1, '2026-11-10 09:28:00', 18, 4, 2),
(5, 'B002', '2026-11-10 09:20:00', 2, '2026-11-10 09:36:00', 16, 5, 2),
(6, 'C001', '2026-11-10 10:00:00', 1, '2026-11-10 10:12:00', 12, 6, 3);
INSERT IGNORE INTO atendimento (id_atendimento, hr_inicio, hr_fim, status_atendimento, id_entrad_fila, id_guiche, id_atendente) VALUES
(1, '2026-11-10 08:55:00', '2026-11-10 09:15:00', 'CONCLUIDO', 1, 1, 1),
(2, '2026-11-10 09:16:00', '2026-11-10 09:36:00', 'CONCLUIDO', 2, 1, 1),
(3, '2026-11-10 09:37:00', '2026-11-10 09:57:00', 'CONCLUIDO', 3, 1, 1),
(4, '2026-11-10 09:28:00', '2026-11-10 09:43:00', 'CONCLUIDO', 4, 2, 2),
(5, '2026-11-10 09:44:00', '2026-11-10 09:59:00', 'CONCLUIDO', 5, 2, 2),
(6, '2026-11-10 10:12:00', '2026-11-10 10:24:00', 'CONCLUIDO', 6, 3, 3);
INSERT IGNORE INTO avaliacao (id_avaliacao, nota, comentario, id_atendimento) VALUES
(1, 5, 'Atendimento muito rapido', 1), (2, 4, 'Bom atendimento', 2), (3, 5, 'Excelente!', 3),
(4, 4, 'Tudo certo no caixa', 4), (5, 3, 'Um pouco demorado', 5), (6, 5, 'Documento emitido na hora', 6);
"""

def criar_e_popular_banco():
    conn = conectar(usar_banco=False)
    cursor = conn.cursor()
    for stmt in (DDL_SCRIPT + DML_SCRIPT).split(";"):
        if stmt.strip():
            cursor.execute(stmt)
    conn.commit()
    cursor.close()
    conn.close()
    print("\n[OK] Banco 'SGFI' criado com sucesso!")

def eliminar_todas_tabelas():
    conn = conectar(usar_banco=True)
    cursor = conn.cursor()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    tabelas = [
        "avaliacao", "atendimento", "entra_fila", "notificacao", "guiche",
        "atendente", "cliente", "servico_fila", "unidade_servico", "fila",
        "servico", "relatorio", "configuracao", "administrador",
        "horar_funcionamento", "unidade", "estabelecimento"
    ]
    for t in tabelas:
        cursor.execute(f"DROP TABLE IF EXISTS {t};")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    conn.commit()
    cursor.close()
    conn.close()
    print("\n[OK] Todas as tabelas foram eliminadas do banco 'SGFI'!")