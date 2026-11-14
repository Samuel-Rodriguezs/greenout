-- Participacao de cada cargo na folha atual: percentual e percentual acumulado (SUM OVER) com ROW_NUMBER.
WITH por_cargo AS (
  SELECT c.nome AS cargo, SUM(s.valor) AS total
  FROM funcionarios f
  JOIN cargos c ON c.id = f.cargo_id
  JOIN salarios s ON s.funcionario_id = f.id
  WHERE s.vigencia_inicio = (SELECT MAX(vigencia_inicio) FROM salarios WHERE funcionario_id = f.id)
  GROUP BY c.id
)
SELECT ROW_NUMBER() OVER (ORDER BY total DESC) AS n, cargo, total,
       ROUND(total * 100.0 / SUM(total) OVER (), 1) AS pct,
       ROUND(SUM(total) OVER (ORDER BY total DESC) * 100.0 / SUM(total) OVER (), 1) AS pct_acum
FROM por_cargo
ORDER BY n;
