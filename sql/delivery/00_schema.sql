-- Schema e dados de delivery/restaurantes: clientes, restaurantes, pratos, entregadores,
-- pedidos (com itens) e avaliacoes. Datas no formato 'AAAA-MM-DD HH:MM'.
CREATE TABLE clientes (id INTEGER PRIMARY KEY, nome TEXT NOT NULL, cidade TEXT NOT NULL);
CREATE TABLE restaurantes (id INTEGER PRIMARY KEY, nome TEXT NOT NULL, culinaria TEXT NOT NULL);
CREATE TABLE pratos (
  id INTEGER PRIMARY KEY, restaurante_id INTEGER NOT NULL REFERENCES restaurantes(id),
  nome TEXT NOT NULL, preco REAL NOT NULL);
CREATE TABLE entregadores (id INTEGER PRIMARY KEY, nome TEXT NOT NULL);
CREATE TABLE pedidos (
  id INTEGER PRIMARY KEY, cliente_id INTEGER NOT NULL REFERENCES clientes(id),
  restaurante_id INTEGER NOT NULL REFERENCES restaurantes(id),
  entregador_id INTEGER NOT NULL REFERENCES entregadores(id),
  data_hora TEXT NOT NULL, entregue_em TEXT, status TEXT NOT NULL, taxa_entrega REAL NOT NULL);
CREATE TABLE itens_pedido (
  pedido_id INTEGER NOT NULL REFERENCES pedidos(id),
  prato_id INTEGER NOT NULL REFERENCES pratos(id), qtd INTEGER NOT NULL,
  PRIMARY KEY (pedido_id, prato_id));
CREATE TABLE avaliacoes (
  id INTEGER PRIMARY KEY, pedido_id INTEGER NOT NULL REFERENCES pedidos(id), nota INTEGER NOT NULL);

INSERT INTO clientes VALUES (1,'Alice','Sao Paulo'),(2,'Bernardo','Sao Paulo'),(3,'Clara','Rio de Janeiro'),
 (4,'Davi','Sao Paulo'),(5,'Elisa','Rio de Janeiro');
INSERT INTO restaurantes VALUES (1,'Trattoria Roma','italiana'),(2,'Sushi Kyoto','japonesa'),(3,'Burger Lab','hamburguer');
INSERT INTO pratos VALUES (1,1,'Lasanha',42),(2,1,'Risoto',48),(3,1,'Pizza Margherita',55),
 (4,2,'Combo Sushi',68),(5,2,'Temaki',24),(6,2,'Yakisoba',38),(7,3,'Cheeseburger',32),(8,3,'Batata Frita',18);
INSERT INTO entregadores VALUES (1,'Rafael'),(2,'Simone'),(3,'Tiago');
INSERT INTO pedidos VALUES
 (1,1,1,1,'2025-05-02 12:10','2025-05-02 12:50','entregue',6),
 (2,1,2,2,'2025-05-09 20:00','2025-05-09 20:35','entregue',8),
 (3,2,1,1,'2025-05-10 19:30','2025-05-10 20:20','entregue',6),
 (4,2,3,3,'2025-05-17 13:00','2025-05-17 13:25','entregue',5),
 (5,3,2,2,'2025-05-18 20:15',NULL,'cancelado',8),
 (6,3,1,3,'2025-05-24 12:30','2025-05-24 13:05','entregue',6),
 (7,4,3,1,'2025-05-25 21:00','2025-05-25 21:30','entregue',5),
 (8,1,1,2,'2025-06-01 12:20','2025-06-01 12:55','entregue',6),
 (9,4,3,3,'2025-06-07 12:45','2025-06-07 13:10','entregue',5),
 (10,2,2,2,'2025-06-08 19:50','2025-06-08 20:40','entregue',8),
 (11,1,3,1,'2025-06-14 20:30','2025-06-14 21:10','entregue',5);
INSERT INTO itens_pedido VALUES
 (1,1,2),(1,2,1),(2,4,1),(2,5,2),(3,3,1),(3,1,1),(4,7,2),(4,8,1),(5,4,1),(6,2,1),(6,3,1),
 (7,7,1),(7,8,2),(8,1,1),(8,3,1),(9,7,3),(10,6,2),(10,5,1),(11,7,2),(11,8,2);
INSERT INTO avaliacoes VALUES (1,1,5),(2,2,4),(3,3,3),(4,4,5),(5,6,4),(6,7,5),(7,8,5),(8,9,3),(9,10,2),(10,11,4);
