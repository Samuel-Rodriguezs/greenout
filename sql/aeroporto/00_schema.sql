-- Aeroporto/Voos: aeronaves, voos, passageiros, tarifas e reservas.
CREATE TABLE aeronaves (id INTEGER PRIMARY KEY, modelo TEXT NOT NULL, capacidade INTEGER NOT NULL);
CREATE TABLE voos (id INTEGER PRIMARY KEY, codigo TEXT NOT NULL, origem TEXT NOT NULL, destino TEXT NOT NULL,
  partida TEXT NOT NULL, aeronave_id INTEGER REFERENCES aeronaves(id), duracao_min INTEGER);
CREATE TABLE passageiros (id INTEGER PRIMARY KEY, nome TEXT NOT NULL, pais TEXT, programa_fidelidade TEXT);
CREATE TABLE tarifas (id INTEGER PRIMARY KEY, classe TEXT NOT NULL, preco_base REAL NOT NULL);
CREATE TABLE reservas (id INTEGER PRIMARY KEY, voo_id INTEGER REFERENCES voos(id),
  passageiro_id INTEGER REFERENCES passageiros(id), tarifa_id INTEGER REFERENCES tarifas(id),
  valor_pago REAL NOT NULL, status TEXT NOT NULL);

INSERT INTO aeronaves VALUES (1,'A320',180),(2,'B737',160),(3,'E195',118);
INSERT INTO voos VALUES
 (1,'AZ100','GRU','CWB','2025-05-01 08:00',1,60),(2,'AZ101','CWB','GRU','2025-05-01 18:00',1,60),
 (3,'AZ200','GRU','REC','2025-05-02 06:30',2,200),(4,'AZ201','REC','GRU','2025-05-03 07:00',2,200),
 (5,'AZ300','GRU','POA','2025-05-03 12:15',3,110),(6,'AZ301','POA','GRU','2025-05-10 14:00',3,110),
 (7,'AZ400','GRU','CWB','2025-06-02 09:00',1,60),(8,'AZ500','CWB','POA','2025-06-05 10:30',3,70);
INSERT INTO passageiros VALUES
 (1,'Alice Martins','Brasil','gold'),(2,'Bernardo Souza','Brasil',NULL),(3,'Camila Ferreira','Brasil','silver'),
 (4,'Daniel Okafor','Nigéria',NULL),(5,'Emma Schmidt','Alemanha','gold'),(6,'Felipe Araújo','Brasil',NULL);
INSERT INTO tarifas VALUES (1,'economica',300),(2,'executiva',900),(3,'promocional',180);
INSERT INTO reservas VALUES
 (1,1,1,1,300,'confirmada'),(2,1,2,3,180,'confirmada'),(3,1,3,2,900,'confirmada'),
 (4,2,1,1,320,'confirmada'),(5,2,4,3,170,'cancelada'),(6,3,5,2,950,'confirmada'),
 (7,3,6,1,310,'confirmada'),(8,3,2,1,300,'confirmada'),(9,4,5,2,900,'confirmada'),
 (10,4,6,1,330,'confirmada'),(11,5,3,1,290,'confirmada'),(12,5,4,3,180,'confirmada'),
 (13,6,3,1,300,'confirmada'),(14,7,1,2,880,'confirmada'),(15,7,2,3,190,'confirmada'),
 (16,8,6,1,300,'confirmada'),(17,8,5,2,910,'cancelada');
