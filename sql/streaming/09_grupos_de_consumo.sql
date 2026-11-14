-- Usuários divididos em 2 grupos de consumo (NTILE + CASE) com percentual acumulado do total (SUM OVER).
WITH tot AS (
  SELECT u.nome, SUM(v.minutos) AS minutos
  FROM usuarios u JOIN visualizacoes v ON v.usuario_id = u.id
  GROUP BY u.id
)
SELECT nome, minutos,
       CASE NTILE(2) OVER (ORDER BY minutos DESC, nome) WHEN 1 THEN 'intenso' ELSE 'leve' END AS grupo,
       ROUND(100.0 * SUM(minutos) OVER (ORDER BY minutos DESC, nome) / SUM(minutos) OVER (), 1) AS pct_acumulado
FROM tot
ORDER BY minutos DESC, nome;
