-- Ranking do salario atual dentro de cada departamento (CTE + RANK com PARTITION BY).
WITH atual AS (
  SELECT f.nome, f.departamento_id, s.valor
  FROM funcionarios f JOIN salarios s ON s.funcionario_id = f.id
  WHERE s.vigencia_inicio = (SELECT MAX(vigencia_inicio) FROM salarios WHERE funcionario_id = f.id)
)
SELECT d.nome AS departamento, a.nome, a.valor,
       RANK() OVER (PARTITION BY d.id ORDER BY a.valor DESC) AS posicao
FROM atual a JOIN departamentos d ON d.id = a.departamento_id
ORDER BY d.nome, posicao;
