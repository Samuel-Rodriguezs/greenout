-- Schema da escola: turmas, alunos, disciplinas e notas (SQLite)
CREATE TABLE turmas (id INTEGER PRIMARY KEY, nome TEXT NOT NULL);
CREATE TABLE alunos (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    turma_id INTEGER NOT NULL REFERENCES turmas(id)
);
CREATE TABLE disciplinas (id INTEGER PRIMARY KEY, nome TEXT NOT NULL);
CREATE TABLE notas (
    id INTEGER PRIMARY KEY,
    aluno_id INTEGER NOT NULL REFERENCES alunos(id),
    disciplina_id INTEGER NOT NULL REFERENCES disciplinas(id),
    nota REAL NOT NULL
);

INSERT INTO turmas VALUES (1,'1A'),(2,'1B');
INSERT INTO alunos VALUES (1,'Ana',1),(2,'Bruno',1),(3,'Carla',1),(4,'Diego',2),(5,'Elisa',2),(6,'Fábio',2);
INSERT INTO disciplinas VALUES (1,'Matemática'),(2,'Português');
INSERT INTO notas VALUES
 (1,1,1,9.0),(2,1,2,8.0),
 (3,2,1,5.0),(4,2,2,6.0),
 (5,3,1,7.0),(6,3,2,7.0),
 (7,4,1,4.0),(8,4,2,5.0),
 (9,5,1,9.0),(10,5,2,8.0),
 (11,6,1,6.0),(12,6,2,8.0);
