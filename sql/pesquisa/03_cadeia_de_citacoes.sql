-- Todos os artigos que influenciam "Modelos Pequenos" (id 11), direta ou indiretamente, via CTE recursiva no grafo de citações.
WITH RECURSIVE cadeia(artigo_id, profundidade) AS (
  SELECT citado_id, 1 FROM citacoes WHERE citante_id = 11
  UNION ALL
  SELECT c.citado_id, ch.profundidade + 1
  FROM citacoes c JOIN cadeia ch ON c.citante_id = ch.artigo_id
)
SELECT a.titulo, a.ano, MIN(ch.profundidade) AS distancia
FROM cadeia ch
JOIN artigos a ON a.id = ch.artigo_id
GROUP BY a.id
ORDER BY distancia, a.ano, a.titulo;
