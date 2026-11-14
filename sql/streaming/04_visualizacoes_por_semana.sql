-- Visualizações por semana, das semanas de 2025-01-06 a 2025-03-03, inclusive semanas vazias (CTE recursiva + LEFT JOIN).
WITH RECURSIVE semanas(inicio) AS (
  SELECT '2025-01-06'
  UNION ALL
  SELECT date(inicio, '+7 day') FROM semanas WHERE inicio < '2025-03-03'
)
SELECT s.inicio, COUNT(v.id) AS visualizacoes, COALESCE(SUM(v.minutos), 0) AS minutos
FROM semanas s
LEFT JOIN visualizacoes v ON v.data >= s.inicio AND v.data < date(s.inicio, '+7 day')
GROUP BY s.inicio
ORDER BY s.inicio;
