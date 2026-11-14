-- Schema da biblioteca: autores, livros, usuários e empréstimos (SQLite)
CREATE TABLE autores (id INTEGER PRIMARY KEY, nome TEXT NOT NULL);
CREATE TABLE livros (
    id INTEGER PRIMARY KEY,
    titulo TEXT NOT NULL,
    autor_id INTEGER NOT NULL REFERENCES autores(id),
    ano INTEGER,
    copias INTEGER NOT NULL
);
CREATE TABLE usuarios (id INTEGER PRIMARY KEY, nome TEXT NOT NULL);
CREATE TABLE emprestimos (
    id INTEGER PRIMARY KEY,
    livro_id INTEGER NOT NULL REFERENCES livros(id),
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
    data_emprestimo TEXT NOT NULL,
    data_prevista TEXT NOT NULL,
    data_devolucao TEXT
);

INSERT INTO autores VALUES (1,'Machado de Assis'),(2,'Clarice Lispector'),(3,'Jorge Amado');
INSERT INTO livros VALUES
 (1,'Dom Casmurro',1,1899,2),
 (2,'Memórias Póstumas',1,1881,1),
 (3,'A Hora da Estrela',2,1977,1),
 (4,'Capitães da Areia',3,1937,2),
 (5,'Gabriela',3,1958,1),
 (6,'Perto do Coração Selvagem',2,1943,1);
INSERT INTO usuarios VALUES (1,'Ana'),(2,'Bruno'),(3,'Carla'),(4,'Diego');
INSERT INTO emprestimos VALUES
 (1,1,1,'2024-01-05','2024-01-19','2024-01-18'),
 (2,1,2,'2024-02-01','2024-02-15','2024-02-20'),
 (3,3,1,'2024-02-10','2024-02-24',NULL),
 (4,4,3,'2024-03-01','2024-03-15','2024-03-10'),
 (5,1,3,'2024-03-05','2024-03-19',NULL),
 (6,2,1,'2024-03-20','2024-04-03',NULL),
 (7,4,2,'2024-03-22','2024-04-05',NULL),
 (8,5,1,'2024-03-25','2024-04-08',NULL);
