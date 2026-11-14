-- Streaming: usuários, títulos (séries e filmes), episódios, visualizações e avaliações.
CREATE TABLE usuarios (id INTEGER PRIMARY KEY, nome TEXT NOT NULL, plano TEXT NOT NULL, pais TEXT, cadastro TEXT);
CREATE TABLE titulos (id INTEGER PRIMARY KEY, nome TEXT NOT NULL, tipo TEXT NOT NULL, genero TEXT, ano INTEGER);
CREATE TABLE episodios (id INTEGER PRIMARY KEY, titulo_id INTEGER REFERENCES titulos(id), temporada INTEGER,
  numero INTEGER, duracao_min INTEGER);
CREATE TABLE visualizacoes (id INTEGER PRIMARY KEY, usuario_id INTEGER REFERENCES usuarios(id),
  episodio_id INTEGER REFERENCES episodios(id), data TEXT NOT NULL, minutos INTEGER NOT NULL);
CREATE TABLE avaliacoes (id INTEGER PRIMARY KEY, usuario_id INTEGER REFERENCES usuarios(id),
  titulo_id INTEGER REFERENCES titulos(id), nota INTEGER NOT NULL);

INSERT INTO usuarios VALUES
 (1,'Ana','premium','BR','2024-01-15'),(2,'Beto','basico','BR','2024-03-20'),(3,'Cris','premium','PT','2024-06-01'),
 (4,'Duda','basico','BR','2024-09-10'),(5,'Edu','padrao','PT','2025-01-05');
INSERT INTO titulos VALUES
 (1,'Noite Eterna','serie','drama',2022),(2,'Codigo Zero','serie','ficcao',2023),(3,'Riso Facil','serie','comedia',2021),
 (4,'O Ultimo Farol','filme','drama',2020),(5,'Orbita','filme','ficcao',2024);
INSERT INTO episodios VALUES
 (1,1,1,1,50),(2,1,1,2,48),(3,1,2,1,52),(4,2,1,1,45),(5,2,1,2,47),
 (6,3,1,1,25),(7,3,1,2,24),(8,3,1,3,26),(9,4,1,1,110),(10,5,1,1,125);
INSERT INTO visualizacoes VALUES
 (1,1,1,'2025-01-10',50),(2,1,2,'2025-01-11',48),(3,1,3,'2025-01-18',30),(4,1,4,'2025-02-02',45),
 (5,1,9,'2025-02-14',110),(6,2,6,'2025-01-10',25),(7,2,7,'2025-01-10',24),(8,2,8,'2025-01-12',26),
 (9,2,1,'2025-02-01',20),(10,3,4,'2025-01-20',45),(11,3,5,'2025-01-21',47),(12,3,10,'2025-02-03',125),
 (13,4,6,'2025-02-05',25),(14,4,10,'2025-02-06',60),(15,5,1,'2025-02-10',50),(16,5,2,'2025-02-11',48),
 (17,5,3,'2025-02-12',52),(18,5,9,'2025-03-01',110),(19,3,1,'2025-03-02',50);
INSERT INTO avaliacoes VALUES
 (1,1,1,5),(2,1,4,4),(3,2,3,4),(4,3,2,5),(5,3,5,3),(6,4,3,3),(7,5,1,4),(8,5,4,5),(9,1,2,4),(10,2,1,3);
