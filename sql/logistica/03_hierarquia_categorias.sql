-- Árvore de categorias com CTE recursiva (nível e caminho) e quantidade de produtos diretos de cada categoria.
WITH RECURSIVE arvore(id, nome, nivel, caminho) AS (
  SELECT id, nome, 0, nome FROM categorias WHERE pai_id IS NULL
  UNION ALL
  SELECT c.id, c.nome, t.nivel + 1, t.caminho || ' > ' || c.nome
  FROM categorias c JOIN arvore t ON c.pai_id = t.id
)
SELECT t.caminho, t.nivel, COUNT(p.id) AS produtos
FROM arvore t
LEFT JOIN produtos p ON p.categoria_id = t.id
GROUP BY t.id
ORDER BY t.caminho;
