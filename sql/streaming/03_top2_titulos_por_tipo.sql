-- Top 2 títulos mais assistidos (em minutos) por tipo: série ou filme (ROW_NUMBER com PARTITION BY).
WITH total AS (
  SELECT t.tipo, t.nome, SUM(v.minutos) AS minutos
  FROM titulos t
  JOIN episodios e ON e.titulo_id = t.id
  JOIN visualizacoes v ON v.episodio_id = e.id
  GROUP BY t.id
), ranq AS (
  SELECT tipo, nome, minutos,
         ROW_NUMBER() OVER (PARTITION BY tipo ORDER BY minutos DESC, nome) AS pos
  FROM total
)
SELECT tipo, nome, minutos FROM ranq WHERE pos <= 2 ORDER BY tipo, pos;
