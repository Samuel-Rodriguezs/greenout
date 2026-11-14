-- Gasto total (consultas realizadas + exames) por paciente, dividido em 3 faixas com NTILE e rotulado com CASE.
WITH gasto AS (
  SELECT p.nome,
         SUM(c.valor) + COALESCE((SELECT SUM(e.custo) FROM exames e
                                  JOIN consultas c2 ON c2.id = e.consulta_id
                                  WHERE c2.paciente_id = p.id AND c2.status = 'realizada'), 0) AS total
  FROM pacientes p JOIN consultas c ON c.paciente_id = p.id AND c.status = 'realizada'
  GROUP BY p.id
), faixa AS (
  SELECT nome, total, NTILE(3) OVER (ORDER BY total DESC, nome) AS n FROM gasto
)
SELECT nome, total,
       CASE n WHEN 1 THEN 'alto' WHEN 2 THEN 'medio' ELSE 'baixo' END AS faixa
FROM faixa ORDER BY total DESC, nome;
