-- Schema e dados de RH e folha de pagamento: departamentos, cargos (hierarquia),
-- funcionarios, historico salarial, ferias, ponto e afastamentos. Data de referencia: 2025-06-30.
CREATE TABLE departamentos (id INTEGER PRIMARY KEY, nome TEXT NOT NULL);
CREATE TABLE cargos (id INTEGER PRIMARY KEY, nome TEXT NOT NULL, superior_id INTEGER REFERENCES cargos(id));
CREATE TABLE funcionarios (
  id INTEGER PRIMARY KEY, nome TEXT NOT NULL,
  cargo_id INTEGER NOT NULL REFERENCES cargos(id),
  departamento_id INTEGER NOT NULL REFERENCES departamentos(id),
  admissao TEXT NOT NULL);
CREATE TABLE salarios (
  id INTEGER PRIMARY KEY, funcionario_id INTEGER NOT NULL REFERENCES funcionarios(id),
  valor REAL NOT NULL, vigencia_inicio TEXT NOT NULL);
CREATE TABLE ferias (
  id INTEGER PRIMARY KEY, funcionario_id INTEGER NOT NULL REFERENCES funcionarios(id),
  inicio TEXT NOT NULL, fim TEXT NOT NULL);
CREATE TABLE ponto (
  id INTEGER PRIMARY KEY, funcionario_id INTEGER NOT NULL REFERENCES funcionarios(id),
  data TEXT NOT NULL, horas REAL NOT NULL);
CREATE TABLE afastamentos (
  id INTEGER PRIMARY KEY, funcionario_id INTEGER NOT NULL REFERENCES funcionarios(id),
  tipo TEXT NOT NULL, inicio TEXT NOT NULL, fim TEXT);

INSERT INTO departamentos VALUES (1,'Tecnologia'),(2,'Financeiro'),(3,'Comercial'),(4,'Juridico');
INSERT INTO cargos VALUES (1,'Diretor',NULL),(2,'Gerente',1),(3,'Coordenador',2),(4,'Analista',3),(5,'Assistente',4);
INSERT INTO funcionarios VALUES
 (1,'Carla Mendes',1,1,'2018-03-01'),(2,'Diego Alves',2,1,'2019-06-10'),
 (3,'Elaine Souza',2,2,'2020-01-15'),(4,'Fabio Lima',3,1,'2021-04-05'),
 (5,'Gina Rocha',4,1,'2022-02-14'),(6,'Hugo Prado',4,2,'2022-08-01'),
 (7,'Iara Nunes',5,3,'2023-05-20'),(8,'Joao Teles',5,1,'2024-01-08');
INSERT INTO salarios VALUES
 (1,1,15000,'2018-03-01'),(2,1,18000,'2022-01-01'),
 (3,2,9000,'2019-06-10'),(4,2,11000,'2021-07-01'),(5,2,12500,'2023-07-01'),
 (6,3,10000,'2020-01-15'),(7,3,11500,'2022-03-01'),
 (8,4,6000,'2021-04-05'),(9,4,7000,'2023-01-01'),
 (10,5,4500,'2022-02-14'),(11,5,5200,'2024-03-01'),
 (12,6,4200,'2022-08-01'),
 (13,7,2500,'2023-05-20'),(14,7,2800,'2024-06-01'),
 (15,8,2400,'2024-01-08');
INSERT INTO ferias VALUES
 (1,1,'2025-01-06','2025-01-25'),(2,2,'2024-12-16','2025-01-04'),
 (3,3,'2025-02-03','2025-02-12'),(4,4,'2025-05-05','2025-05-24'),
 (5,5,'2025-04-07','2025-04-21');
INSERT INTO ponto VALUES
 (1,5,'2025-03-10',9.5),(2,5,'2025-03-11',8),(3,5,'2025-03-12',10),
 (4,8,'2025-03-10',8),(5,8,'2025-03-11',11),(6,8,'2025-03-12',8.5),
 (7,4,'2025-03-10',7.5),(8,4,'2025-03-11',8),
 (9,6,'2025-03-10',8),(10,6,'2025-03-11',8),
 (11,7,'2025-03-10',9),(12,7,'2025-03-11',9),(13,7,'2025-03-12',8);
INSERT INTO afastamentos VALUES
 (1,5,'licenca medica','2025-05-02','2025-05-11'),
 (2,7,'licenca medica','2025-02-10','2025-02-14'),
 (3,7,'licenca maternidade','2025-06-01',NULL),
 (4,8,'licenca medica','2025-04-01','2025-04-03'),
 (5,3,'treinamento','2025-03-17','2025-03-21'),
 (6,5,'treinamento','2025-06-09','2025-06-13');
