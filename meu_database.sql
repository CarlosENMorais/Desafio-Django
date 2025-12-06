
CREATE TABLE Aluno (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    cpf VARCHAR(11) UNIQUE NOT NULL,
    data_de_ingresso DATE NOT NULL
);

CREATE TABLE Curso (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    carga_horaria INTEGER NOT NULL,
    valor_da_inscrissao NUMERIC(10, 2) NOT NULL,
    status BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE Matricula (
    id SERIAL PRIMARY KEY,    
    aluno_id INTEGER NOT NULL,
        CONSTRAINT fk_aluno
        FOREIGN KEY (aluno_id)
        REFERENCES Aluno (id)
        ON DELETE RESTRICT,
    curso_id INTEGER NOT NULL,
        CONSTRAINT fk_curso
        FOREIGN KEY (curso_id)
        REFERENCES Curso (id)
        ON DELETE RESTRICT,
    data_matricula DATE NOT NULL,
    pago BOOLEAN NOT NULL DEFAULT FALSE,
        CONSTRAINT unique_aluno_curso
        UNIQUE (aluno_id, curso_id)
);