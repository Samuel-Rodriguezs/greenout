-- Pesquisa acadêmica: instituições, pesquisadores (com orientação), áreas (hierarquia), periódicos, artigos, autorias,
-- citações entre artigos (grafo dirigido) e financiamentos. Data de referência nas consultas: 2025-06-15.
CREATE TABLE instituicoes (id INTEGER PRIMARY KEY, nome TEXT NOT NULL, pais TEXT);
CREATE TABLE pesquisadores (id INTEGER PRIMARY KEY, nome TEXT NOT NULL, instituicao_id INTEGER REFERENCES instituicoes(id),
  orientador_id INTEGER REFERENCES pesquisadores(id));
CREATE TABLE areas (id INTEGER PRIMARY KEY, nome TEXT NOT NULL, pai_id INTEGER REFERENCES areas(id));
CREATE TABLE periodicos (id INTEGER PRIMARY KEY, nome TEXT NOT NULL, fator REAL);
CREATE TABLE artigos (id INTEGER PRIMARY KEY, titulo TEXT NOT NULL, ano INTEGER, periodico_id INTEGER REFERENCES periodicos(id),
  area_id INTEGER REFERENCES areas(id));
CREATE TABLE autorias (artigo_id INTEGER REFERENCES artigos(id), pesquisador_id INTEGER REFERENCES pesquisadores(id), ordem INTEGER,
  PRIMARY KEY (artigo_id, pesquisador_id));
CREATE TABLE citacoes (citante_id INTEGER REFERENCES artigos(id), citado_id INTEGER REFERENCES artigos(id),
  PRIMARY KEY (citante_id, citado_id));
CREATE TABLE financiamentos (id INTEGER PRIMARY KEY, pesquisador_id INTEGER REFERENCES pesquisadores(id), agencia TEXT,
  valor REAL, inicio TEXT, fim TEXT);

INSERT INTO instituicoes VALUES (1,'USP','Brasil'),(2,'UNICAMP','Brasil'),(3,'MIT','EUA'),(4,'ETH Zurique','Suíça');
INSERT INTO pesquisadores VALUES (1,'Ana Prado',1,NULL),(2,'Bruno Castro',1,1),(3,'Carla Mendes',2,1),(4,'Diego Ramos',2,2),
  (5,'Elena Fischer',4,NULL),(6,'Felipe Tanaka',3,NULL),(7,'Gabi Alves',1,3),(8,'Hugo Lima',3,6);
INSERT INTO areas VALUES (1,'Computação',NULL),(2,'Inteligência Artificial',1),(3,'Redes',1),(4,'Biologia',NULL),(5,'Genômica',4),
  (6,'Aprendizado Profundo',2);
INSERT INTO periodicos VALUES (1,'Journal of AI',8.5),(2,'Network Letters',3.2),(3,'Genome Review',12.1),(4,'Revista Brasileira de Computação',1.1);
INSERT INTO artigos VALUES
 (1,'Redes Neurais Esparsas',2018,1,6),(2,'Atenção Eficiente',2019,1,6),(3,'Roteamento Adaptativo',2019,2,3),
 (4,'Sequenciamento Rápido',2020,3,5),(5,'Poda de Modelos',2021,1,2),(6,'Redes Definidas por Software',2021,2,3),
 (7,'Edição Genômica Segura',2022,3,5),(8,'Treinamento Federado',2022,1,6),(9,'Compressão de Embeddings',2023,4,2),
 (10,'Anotação Automática de Genes',2023,3,5),(11,'Modelos Pequenos',2024,1,2),(12,'Latência em Redes 6G',2024,2,3);
INSERT INTO autorias VALUES
 (1,1,1),(1,2,2),(2,1,1),(2,3,2),(3,3,1),(3,4,2),(4,5,1),(4,7,2),(5,2,1),(5,4,2),(5,1,3),(6,3,1),(6,7,2),
 (7,5,1),(7,6,2),(8,2,1),(8,8,2),(9,4,1),(10,5,1),(10,7,2),(11,1,1),(11,2,2),(11,8,3),(12,3,1),(12,4,2);
INSERT INTO citacoes VALUES
 (2,1),(5,1),(5,2),(8,1),(8,2),(8,5),(9,5),(11,5),(11,8),(11,9),(11,1),(6,3),(12,3),(12,6),(7,4),(10,4),(10,7);
INSERT INTO financiamentos VALUES
 (1,1,'FAPESP',400000,'2022-01-01','2025-12-31'),(2,3,'CNPq',150000,'2023-03-01','2025-02-28'),
 (3,5,'SNSF',600000,'2021-09-01','2026-08-31'),(4,6,'NSF',500000,'2024-01-01','2027-12-31'),
 (5,2,'FAPESP',250000,'2023-07-01','2025-06-30'),(6,1,'CNPq',120000,'2020-01-01','2022-12-31');
