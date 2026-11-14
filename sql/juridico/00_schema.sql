-- Escritório jurídico: clientes, advogados (com hierarquia de sócios), processos, partes, andamentos, prazos, audiências, honorários e parcelas.
-- Data de referência usada nas consultas: 2025-06-15.
CREATE TABLE clientes (id INTEGER PRIMARY KEY, nome TEXT NOT NULL, tipo TEXT, cidade TEXT);
CREATE TABLE advogados (id INTEGER PRIMARY KEY, nome TEXT NOT NULL, oab TEXT, socio_id INTEGER REFERENCES advogados(id));
CREATE TABLE processos (id INTEGER PRIMARY KEY, numero TEXT, cliente_id INTEGER REFERENCES clientes(id),
  advogado_id INTEGER REFERENCES advogados(id), area TEXT, status TEXT, abertura TEXT, valor_causa REAL);
CREATE TABLE partes (id INTEGER PRIMARY KEY, processo_id INTEGER REFERENCES processos(id), nome TEXT, papel TEXT);
CREATE TABLE andamentos (id INTEGER PRIMARY KEY, processo_id INTEGER REFERENCES processos(id), data TEXT, tipo TEXT);
CREATE TABLE prazos (id INTEGER PRIMARY KEY, processo_id INTEGER REFERENCES processos(id), descricao TEXT, vencimento TEXT, cumprido INTEGER);
CREATE TABLE audiencias (id INTEGER PRIMARY KEY, processo_id INTEGER REFERENCES processos(id), data TEXT, tipo TEXT);
CREATE TABLE honorarios (id INTEGER PRIMARY KEY, processo_id INTEGER REFERENCES processos(id), valor_total REAL);
CREATE TABLE parcelas (id INTEGER PRIMARY KEY, honorario_id INTEGER REFERENCES honorarios(id), numero INTEGER,
  vencimento TEXT, valor REAL, pago_em TEXT);

INSERT INTO clientes VALUES (1,'Construtora Alfa','PJ','São Paulo'),(2,'Maria Souza','PF','Campinas'),(3,'João Pereira','PF','São Paulo'),
  (4,'Mercado Beta','PJ','Santos'),(5,'Clínica Gama','PJ','São Paulo'),(6,'Lucas Dias','PF','Campinas');
INSERT INTO advogados VALUES (1,'Helena Barros','OAB-SP 1001',NULL),(2,'Rui Matos','OAB-SP 1002',1),(3,'Clara Nunes','OAB-SP 1003',1),
  (4,'Pedro Lacerda','OAB-SP 1004',2),(5,'Joana Pires','OAB-SP 1005',2);
INSERT INTO processos VALUES
 (1,'0001-2024',1,2,'Civil','ativo','2024-02-10',500000),(2,'0002-2024',1,4,'Trabalhista','ativo','2024-05-03',80000),
 (3,'0003-2023',2,3,'Família','ativo','2023-11-20',120000),(4,'0004-2025',3,5,'Trabalhista','ativo','2025-01-15',45000),
 (5,'0005-2022',4,2,'Tributário','arquivado','2022-08-01',900000),(6,'0006-2025',4,4,'Civil','ativo','2025-03-09',60000),
 (7,'0007-2024',5,1,'Tributário','ativo','2024-09-12',1500000),(8,'0008-2025',2,3,'Civil','ativo','2025-04-22',30000),
 (9,'0009-2023',1,2,'Tributário','encerrado','2023-03-14',250000);
INSERT INTO partes VALUES
 (1,1,'Construtora Alfa','autor'),(2,1,'Mercado Beta','reu'),(3,2,'Construtora Alfa','reu'),(4,2,'Carlos Ferreira','autor'),
 (5,3,'Maria Souza','autor'),(6,3,'Antônio Souza','reu'),(7,4,'João Pereira','autor'),(8,4,'Oficina Delta','reu'),
 (9,5,'Mercado Beta','autor'),(10,5,'Fazenda Estadual','reu'),(11,6,'Mercado Beta','autor'),(12,6,'Clínica Gama','reu'),
 (13,7,'Clínica Gama','autor'),(14,7,'Fazenda Estadual','reu'),(15,8,'Maria Souza','autor'),(16,8,'Oficina Delta','reu'),
 (17,9,'Construtora Alfa','autor'),(18,9,'Fazenda Municipal','reu');
INSERT INTO andamentos VALUES
 (1,1,'2024-02-10','distribuição'),(2,1,'2024-03-05','contestação'),(3,1,'2024-06-20','perícia'),(4,1,'2025-02-11','sentença'),
 (5,2,'2024-05-03','distribuição'),(6,2,'2024-07-15','audiência'),(7,2,'2025-01-10','sentença'),
 (8,3,'2023-11-20','distribuição'),(9,3,'2024-01-30','despacho'),(10,3,'2025-05-02','perícia'),
 (11,7,'2024-09-12','distribuição'),(12,7,'2024-10-01','liminar'),(13,7,'2025-04-15','recurso');
INSERT INTO prazos VALUES
 (1,1,'Apelação','2025-06-20',0),(2,2,'Recurso ordinário','2025-06-12',0),(3,3,'Laudo pericial','2025-06-30',0),
 (4,4,'Réplica','2025-06-16',0),(5,6,'Contestação','2025-07-10',0),(6,7,'Contrarrazões','2025-06-15',0),
 (7,8,'Emenda inicial','2025-05-30',1),(8,1,'Memoriais','2025-08-01',0);
INSERT INTO audiencias VALUES (1,2,'2024-07-15','instrução'),(2,1,'2025-06-25','conciliação'),(3,3,'2025-07-08','instrução'),
 (4,7,'2025-09-02','julgamento'),(5,4,'2025-03-10','conciliação');
INSERT INTO honorarios VALUES (1,1,30000),(2,2,9000),(3,3,12000),(4,4,4500),(5,7,60000),(6,9,15000);
INSERT INTO parcelas VALUES
 (1,1,1,'2025-04-10',10000,'2025-04-09'),(2,1,2,'2025-05-10',10000,'2025-05-25'),(3,1,3,'2025-06-10',10000,NULL),
 (4,2,1,'2025-03-05',3000,'2025-03-05'),(5,2,2,'2025-04-05',3000,NULL),(6,2,3,'2025-05-05',3000,NULL),
 (7,3,1,'2025-02-20',3000,'2025-02-20'),(8,3,2,'2025-03-20',3000,'2025-03-22'),(9,3,3,'2025-04-20',3000,'2025-04-20'),
 (10,3,4,'2025-05-20',3000,'2025-06-01'),
 (11,4,1,'2025-05-15',1500,'2025-05-15'),(12,4,2,'2025-06-15',1500,NULL),(13,4,3,'2025-07-15',1500,NULL),
 (14,5,1,'2025-03-01',15000,'2025-03-01'),(15,5,2,'2025-04-01',15000,'2025-04-01'),(16,5,3,'2025-05-01',15000,'2025-05-02'),
 (17,5,4,'2025-06-01',15000,NULL),
 (18,6,1,'2025-01-10',5000,'2025-01-10'),(19,6,2,'2025-02-10',5000,'2025-02-10'),(20,6,3,'2025-03-10',5000,'2025-03-10');
