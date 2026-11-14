-- Schema de finanças pessoais: contas, categorias e lançamentos (SQLite)
-- Convenção: valor positivo = receita, valor negativo = despesa
CREATE TABLE contas (id INTEGER PRIMARY KEY, nome TEXT NOT NULL);
CREATE TABLE categorias (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('receita', 'despesa'))
);
CREATE TABLE lancamentos (
    id INTEGER PRIMARY KEY,
    conta_id INTEGER NOT NULL REFERENCES contas(id),
    categoria_id INTEGER NOT NULL REFERENCES categorias(id),
    data TEXT NOT NULL,
    valor INTEGER NOT NULL,
    descricao TEXT NOT NULL
);

INSERT INTO contas VALUES (1,'Corrente'),(2,'Poupança'),(3,'Carteira');
INSERT INTO categorias VALUES
 (1,'Salário','receita'),(2,'Moradia','despesa'),(3,'Alimentação','despesa'),
 (4,'Lazer','despesa'),(5,'Transporte','despesa'),(6,'Saúde','despesa');
INSERT INTO lancamentos VALUES
 (1,1,1,'2024-01-05',5000,'Salário jan'),
 (2,1,2,'2024-01-10',-1500,'Aluguel jan'),
 (3,1,3,'2024-01-15',-600,'Mercado jan'),
 (4,1,4,'2024-01-20',-200,'Cinema'),
 (5,1,1,'2024-02-05',5000,'Salário fev'),
 (6,1,2,'2024-02-10',-1500,'Aluguel fev'),
 (7,1,3,'2024-02-18',-750,'Mercado fev'),
 (8,1,5,'2024-02-25',-300,'Combustível'),
 (9,2,1,'2024-03-01',1000,'Bônus'),
 (10,1,3,'2024-03-12',-500,'Mercado mar'),
 (11,1,4,'2024-03-15',-350,'Show');
