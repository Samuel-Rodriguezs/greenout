-- Pivot manual: receita de consultas realizadas por especialidade, com uma coluna por mês (strftime + CASE).
SELECT m.especialidade,
  SUM(CASE WHEN strftime('%m', c.data) = '01' THEN c.valor ELSE 0 END) AS jan,
  SUM(CASE WHEN strftime('%m', c.data) = '02' THEN c.valor ELSE 0 END) AS fev,
  SUM(CASE WHEN strftime('%m', c.data) = '03' THEN c.valor ELSE 0 END) AS mar
FROM consultas c JOIN medicos m ON m.id = c.medico_id
WHERE c.status = 'realizada'
GROUP BY m.especialidade
ORDER BY m.especialidade;
