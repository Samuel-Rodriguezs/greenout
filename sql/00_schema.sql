CREATE TABLE departamentos (
    id   INTEGER PRIMARY KEY,
    nome TEXT NOT NULL
);

CREATE TABLE funcionarios (
    id              INTEGER PRIMARY KEY,
    nome            TEXT NOT NULL,
    salario         REAL NOT NULL,
    departamento_id INTEGER REFERENCES departamentos(id)
);

INSERT INTO departamentos (id, nome) VALUES (1, 'TI'), (2, 'RH'), (3, 'Financeiro');

INSERT INTO funcionarios (id, nome, salario, departamento_id) VALUES
    (1, 'Ana',   8000, 1),
    (2, 'Bruno', 6000, 1),
    (3, 'Carla', 5000, 2),
    (4, 'Davi',  7000, 3),
    (5, 'Eva',   4000, NULL);
