-- Schema e dados de uma imobiliaria: proprietarios, imoveis, locatarios, contratos de aluguel,
-- pagamentos mensais e vistorias. Data de referencia das consultas: 2025-06-30.
CREATE TABLE proprietarios (id INTEGER PRIMARY KEY, nome TEXT NOT NULL, cidade TEXT NOT NULL);
CREATE TABLE imoveis (
  id INTEGER PRIMARY KEY, proprietario_id INTEGER NOT NULL REFERENCES proprietarios(id),
  tipo TEXT NOT NULL, bairro TEXT NOT NULL, area REAL NOT NULL, quartos INTEGER NOT NULL,
  valor_aluguel REAL NOT NULL);
CREATE TABLE locatarios (id INTEGER PRIMARY KEY, nome TEXT NOT NULL, renda REAL NOT NULL);
CREATE TABLE contratos (
  id INTEGER PRIMARY KEY, imovel_id INTEGER NOT NULL REFERENCES imoveis(id),
  locatario_id INTEGER NOT NULL REFERENCES locatarios(id),
  inicio TEXT NOT NULL, fim TEXT NOT NULL, valor REAL NOT NULL, dia_venc INTEGER NOT NULL);
CREATE TABLE pagamentos (
  id INTEGER PRIMARY KEY, contrato_id INTEGER NOT NULL REFERENCES contratos(id),
  competencia TEXT NOT NULL, vencimento TEXT NOT NULL, pago_em TEXT, valor REAL NOT NULL);
CREATE TABLE vistorias (
  id INTEGER PRIMARY KEY, imovel_id INTEGER NOT NULL REFERENCES imoveis(id),
  data TEXT NOT NULL, tipo TEXT NOT NULL, nota INTEGER NOT NULL);

INSERT INTO proprietarios VALUES (1,'Marcos Vieira','Sao Paulo'),(2,'Lucia Prado','Sao Paulo'),
 (3,'Antonio Gomes','Rio de Janeiro'),(4,'Sonia Dias','Sao Paulo');
INSERT INTO imoveis VALUES
 (1,1,'apartamento','Centro',60,2,1800),(2,1,'apartamento','Centro',85,3,2500),
 (3,2,'casa','Jardins',150,4,4500),(4,2,'apartamento','Jardins',70,2,2800),
 (5,3,'casa','Centro',120,3,3200),(6,3,'sala','Centro',40,0,1500),
 (7,4,'apartamento','Jardins',55,1,2000),(8,2,'casa','Vila Nova',100,3,2600);
INSERT INTO locatarios VALUES (1,'Ana Beatriz',7000),(2,'Bruno Castro',9000),
 (3,'Camila Dutra',12000),(4,'Daniel Esteves',5000),(5,'Eva Fontes',4000);
INSERT INTO contratos VALUES
 (1,1,1,'2024-01-01','2025-12-31',1800,5),(2,2,2,'2024-07-01','2026-06-30',2500,10),
 (3,3,3,'2025-01-01','2026-12-31',4500,5),(4,4,4,'2024-10-01','2025-09-30',2800,15),
 (5,5,2,'2023-03-01','2025-02-28',3200,10),(6,6,1,'2025-02-01','2026-01-31',1500,5),
 (7,8,4,'2023-06-01','2024-12-31',2600,10);
INSERT INTO pagamentos VALUES
 (1,1,'2025-01','2025-01-05','2025-01-05',1800),(2,1,'2025-02','2025-02-05','2025-02-05',1800),
 (3,1,'2025-03','2025-03-05','2025-03-12',1800),(4,1,'2025-04','2025-04-05','2025-04-05',1800),
 (5,1,'2025-05','2025-05-05','2025-05-05',1800),(6,1,'2025-06','2025-06-05',NULL,1800),
 (7,2,'2025-01','2025-01-10','2025-01-10',2500),(8,2,'2025-02','2025-02-10','2025-02-10',2500),
 (9,2,'2025-03','2025-03-10','2025-03-10',2500),(10,2,'2025-04','2025-04-10','2025-04-20',2500),
 (11,2,'2025-05','2025-05-10','2025-05-10',2500),(12,2,'2025-06','2025-06-10','2025-06-10',2500),
 (13,3,'2025-01','2025-01-05','2025-01-05',4500),(14,3,'2025-04','2025-04-05','2025-04-05',4500),
 (15,3,'2025-05','2025-05-05','2025-05-09',4500),(16,3,'2025-06','2025-06-05','2025-06-05',4500),
 (17,4,'2025-01','2025-01-15','2025-01-15',2800),(18,4,'2025-02','2025-02-15','2025-02-20',2800),
 (19,4,'2025-03','2025-03-15',NULL,2800),(20,4,'2025-04','2025-04-15','2025-04-30',2800),
 (21,4,'2025-05','2025-05-15','2025-05-15',2800),(22,4,'2025-06','2025-06-15',NULL,2800),
 (23,6,'2025-02','2025-02-05','2025-02-05',1500),(24,6,'2025-04','2025-04-05','2025-04-05',1500),
 (25,6,'2025-05','2025-05-05','2025-05-05',1500),(26,6,'2025-06','2025-06-05','2025-06-05',1500),
 (27,5,'2025-01','2025-01-10','2025-01-10',3200),(28,5,'2025-02','2025-02-10','2025-02-10',3200);
INSERT INTO vistorias VALUES
 (1,1,'2024-01-01','entrada',9),(2,1,'2024-12-15','periodica',8),(3,1,'2025-05-20','periodica',6),
 (4,2,'2024-07-01','entrada',10),(5,2,'2025-04-02','periodica',9),(6,3,'2025-01-01','entrada',9),
 (7,4,'2024-10-01','entrada',8),(8,4,'2025-04-10','periodica',8),
 (9,5,'2023-03-01','entrada',7),(10,5,'2025-02-28','saida',4),(11,6,'2025-02-01','entrada',9),
 (12,8,'2023-06-01','entrada',8),(13,8,'2024-12-31','saida',7);
