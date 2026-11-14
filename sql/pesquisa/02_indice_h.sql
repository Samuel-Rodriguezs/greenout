-- Índice h de cada pesquisador calculado em SQL: maior h tal que h artigos têm pelo menos h citações (CTEs + ROW_NUMBER).
WITH citados AS (
  SELECT au.pesquisador_id, au.artigo_id, COUNT(c.citante_id) AS n
  FROM autorias au
  LEFT JOIN citacoes c ON c.citado_id = au.artigo_id
  GROUP BY au.pesquisador_id, au.artigo_id
),
ordenados AS (
  SELECT pesquisador_id, n,
         ROW_NUMBER() OVER (PARTITION BY pesquisador_id ORDER BY n DESC, artigo_id) AS posicao
  FROM citados
)
SELECT p.nome, COUNT(o.posicao) AS artigos, COALESCE(MAX(CASE WHEN o.n >= o.posicao THEN o.posicao END), 0) AS indice_h
FROM pesquisadores p
LEFT JOIN ordenados o ON o.pesquisador_id = p.id
GROUP BY p.id
ORDER BY indice_h DESC, p.nome;
