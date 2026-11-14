-- Dias desde a consulta anterior de cada paciente (LAG + julianday); só quem tem consulta anterior.
WITH h AS (
  SELECT p.nome, c.data,
         LAG(c.data) OVER (PARTITION BY c.paciente_id ORDER BY c.data) AS anterior
  FROM consultas c JOIN pacientes p ON p.id = c.paciente_id
  WHERE c.status = 'realizada'
)
SELECT nome, data, CAST(julianday(data) - julianday(anterior) AS INTEGER) AS dias
FROM h
WHERE anterior IS NOT NULL
ORDER BY nome, data;
