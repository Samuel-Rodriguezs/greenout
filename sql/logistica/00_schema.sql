-- Logística e estoque: depósitos, categorias (hierarquia), produtos, fornecedores, transportadoras, lotes com validade,
-- movimentações (E = entrada, S = saída), pedidos de compra e rotas entre depósitos (grafo dirigido).
-- Data de referência usada nas consultas: 2025-06-15.
CREATE TABLE depositos (id INTEGER PRIMARY KEY, nome TEXT NOT NULL, cidade TEXT);
CREATE TABLE categorias (id INTEGER PRIMARY KEY, nome TEXT NOT NULL, pai_id INTEGER REFERENCES categorias(id));
CREATE TABLE fornecedores (id INTEGER PRIMARY KEY, nome TEXT NOT NULL);
CREATE TABLE transportadoras (id INTEGER PRIMARY KEY, nome TEXT NOT NULL);
CREATE TABLE produtos (id INTEGER PRIMARY KEY, nome TEXT NOT NULL, categoria_id INTEGER REFERENCES categorias(id),
  fornecedor_id INTEGER REFERENCES fornecedores(id), custo REAL);
CREATE TABLE lotes (id INTEGER PRIMARY KEY, produto_id INTEGER REFERENCES produtos(id), deposito_id INTEGER REFERENCES depositos(id),
  codigo TEXT, validade TEXT);
CREATE TABLE movimentacoes (id INTEGER PRIMARY KEY, lote_id INTEGER REFERENCES lotes(id), tipo TEXT CHECK (tipo IN ('E','S')),
  qtd INTEGER, data TEXT);
CREATE TABLE pedidos_compra (id INTEGER PRIMARY KEY, fornecedor_id INTEGER REFERENCES fornecedores(id),
  deposito_id INTEGER REFERENCES depositos(id), transportadora_id INTEGER REFERENCES transportadoras(id),
  data TEXT, previsto TEXT, entrega TEXT, valor REAL, status TEXT);
CREATE TABLE rotas (id INTEGER PRIMARY KEY, origem_id INTEGER REFERENCES depositos(id), destino_id INTEGER REFERENCES depositos(id),
  transportadora_id INTEGER REFERENCES transportadoras(id), km INTEGER, dias INTEGER);

INSERT INTO depositos VALUES (1,'CD São Paulo','São Paulo'),(2,'CD Campinas','Campinas'),(3,'CD Curitiba','Curitiba'),
  (4,'CD Porto Alegre','Porto Alegre'),(5,'CD Florianópolis','Florianópolis');
INSERT INTO categorias VALUES (1,'Alimentos',NULL),(2,'Bebidas',1),(3,'Laticínios',1),(4,'Limpeza',NULL),(5,'Sucos',2),(6,'Queijos',3);
INSERT INTO fornecedores VALUES (1,'Agro Vale'),(2,'Lácteos Serra'),(3,'Brasil Clean');
INSERT INTO transportadoras VALUES (1,'RodoLeste'),(2,'TransSul'),(3,'Veloz');
INSERT INTO produtos VALUES (1,'Suco de Uva',5,1,4.5),(2,'Suco de Laranja',5,1,3.8),(3,'Queijo Minas',6,2,22),(4,'Iogurte Natural',3,2,2.9),
  (5,'Detergente',4,3,1.8),(6,'Desinfetante',4,3,5.6),(7,'Água Mineral',2,1,1.2),(8,'Queijo Parmesão',6,2,48);
INSERT INTO lotes VALUES (1,1,1,'L001','2025-07-01'),(2,1,2,'L002','2025-12-01'),(3,2,1,'L003','2025-06-20'),(4,3,1,'L004','2025-06-10'),
  (5,4,2,'L005','2025-06-25'),(6,5,3,'L006','2027-01-01'),(7,6,3,'L007','2026-06-01'),(8,7,1,'L008','2026-03-01'),
  (9,7,4,'L009','2026-03-01'),(10,8,2,'L010','2025-11-30'),(11,3,3,'L011','2025-08-30');
INSERT INTO movimentacoes VALUES
 (1,1,'E',200,'2025-04-01'),(2,1,'S',50,'2025-04-20'),(3,1,'S',70,'2025-05-10'),(4,1,'S',30,'2025-06-01'),
 (5,2,'E',300,'2025-05-02'),(6,2,'S',40,'2025-05-20'),
 (7,3,'E',100,'2025-04-10'),(8,3,'S',60,'2025-05-05'),(9,3,'S',40,'2025-05-30'),
 (10,4,'E',80,'2025-03-15'),(11,4,'S',30,'2025-04-02'),(12,4,'S',20,'2025-05-01'),
 (13,5,'E',150,'2025-05-20'),(14,5,'S',100,'2025-06-05'),
 (15,6,'E',500,'2025-02-01'),(16,6,'S',120,'2025-03-01'),(17,6,'S',180,'2025-04-01'),(18,6,'S',100,'2025-05-01'),
 (19,7,'E',250,'2025-03-10'),(20,7,'S',60,'2025-04-10'),
 (21,8,'E',1000,'2025-01-15'),(22,8,'S',400,'2025-02-15'),(23,8,'S',300,'2025-03-15'),(24,8,'S',200,'2025-04-15'),
 (25,9,'E',600,'2025-03-01'),(26,9,'S',150,'2025-04-01'),
 (27,10,'E',40,'2025-04-20'),
 (28,11,'E',60,'2025-05-25'),(29,11,'S',10,'2025-06-02');
INSERT INTO pedidos_compra VALUES
 (1,1,1,1,'2025-03-01','2025-03-10','2025-03-09',5000,'recebido'),(2,1,2,2,'2025-04-01','2025-04-10','2025-04-15',3200,'recebido'),
 (3,2,1,1,'2025-04-05','2025-04-12','2025-04-12',7800,'recebido'),(4,2,3,3,'2025-05-01','2025-05-10','2025-05-10',6400,'recebido'),
 (5,3,3,2,'2025-05-10','2025-05-20','2025-05-22',2100,'recebido'),(6,3,4,2,'2025-05-20','2025-05-30','2025-06-04',1800,'recebido'),
 (7,1,4,3,'2025-06-05','2025-06-12',NULL,2900,'pendente'),(8,2,2,1,'2025-06-10','2025-06-20',NULL,4100,'pendente');
INSERT INTO rotas VALUES (1,1,2,1,100,1),(2,1,3,2,400,2),(3,2,3,1,350,2),(4,3,4,2,710,3),(5,3,5,3,300,1),(6,5,4,3,470,2),(7,4,1,2,1100,4);
