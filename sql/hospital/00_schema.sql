-- Hospital: pacientes, médicos (com hierarquia de chefia), consultas, exames e internações.
CREATE TABLE pacientes (id INTEGER PRIMARY KEY, nome TEXT NOT NULL, nascimento TEXT, sexo TEXT, cidade TEXT);
CREATE TABLE medicos (id INTEGER PRIMARY KEY, nome TEXT NOT NULL, especialidade TEXT, chefe_id INTEGER REFERENCES medicos(id));
CREATE TABLE consultas (id INTEGER PRIMARY KEY, paciente_id INTEGER REFERENCES pacientes(id), medico_id INTEGER REFERENCES medicos(id),
  data TEXT, valor REAL, status TEXT);
CREATE TABLE exames (id INTEGER PRIMARY KEY, consulta_id INTEGER REFERENCES consultas(id), tipo TEXT, custo REAL, resultado TEXT);
CREATE TABLE internacoes (id INTEGER PRIMARY KEY, paciente_id INTEGER REFERENCES pacientes(id), medico_id INTEGER REFERENCES medicos(id),
  entrada TEXT, saida TEXT, motivo TEXT);

INSERT INTO pacientes VALUES
 (1,'Ana Lima','1985-03-10','F','São Paulo'),(2,'Bruno Reis','1972-07-22','M','Campinas'),
 (3,'Carla Dias','1990-11-05','F','São Paulo'),(4,'Diego Melo','2001-01-30','M','Santos'),
 (5,'Elisa Prado','1958-09-14','F','Campinas'),(6,'Fábio Nunes','1966-05-02','M','São Paulo');
INSERT INTO medicos VALUES
 (1,'Helena Costa','Cardiologia',NULL),(2,'Paulo Silva','Cardiologia',1),(3,'Marta Rocha','Ortopedia',1),
 (4,'Ivo Tavares','Clínica Geral',2),(5,'Lia Campos','Clínica Geral',3);
INSERT INTO consultas VALUES
 (1,1,1,'2025-01-10',300,'realizada'),(2,1,4,'2025-02-15',150,'realizada'),(3,2,2,'2025-01-20',250,'realizada'),
 (4,2,2,'2025-03-05',250,'realizada'),(5,3,3,'2025-02-08',280,'realizada'),(6,3,4,'2025-02-28',150,'cancelada'),
 (7,4,4,'2025-03-12',150,'realizada'),(8,5,1,'2025-01-25',300,'realizada'),(9,5,2,'2025-03-18',250,'realizada'),
 (10,6,5,'2025-02-02',150,'realizada'),(11,6,3,'2025-03-22',280,'realizada'),(12,1,1,'2025-03-30',300,'realizada');
INSERT INTO exames VALUES
 (1,1,'Eletrocardiograma',120,'normal'),(2,1,'Hemograma',60,'alterado'),(3,3,'Eletrocardiograma',120,'alterado'),
 (4,4,'Hemograma',60,'normal'),(5,5,'Raio-X',90,'alterado'),(6,8,'Eletrocardiograma',120,'normal'),
 (7,9,'Hemograma',60,'alterado'),(8,11,'Raio-X',90,'normal'),(9,12,'Hemograma',60,'normal'),
 (10,12,'Eletrocardiograma',120,'normal');
INSERT INTO internacoes VALUES
 (1,2,2,'2025-01-21','2025-01-26','arritmia'),(2,5,1,'2025-02-10','2025-02-20','infarto'),
 (3,3,3,'2025-02-09','2025-02-12','fratura'),(4,6,3,'2025-03-23',NULL,'fratura'),
 (5,2,2,'2025-03-06','2025-03-08','arritmia');
