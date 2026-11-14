-- Hierarquia de cargos com CTE recursiva: nivel, caminho e quantidade de funcionarios em cada cargo.
WITH RECURSIVE arvore(id, nome, nivel, caminho) AS (
  SELECT id, nome, 0, nome FROM cargos WHERE superior_id IS NULL
  UNION ALL
  SELECT c.id, c.nome, a.nivel + 1, a.caminho || ' > ' || c.nome
  FROM cargos c JOIN arvore a ON c.superior_id = a.id
)
SELECT a.nome, a.nivel, a.caminho, COUNT(f.id) AS funcionarios
FROM arvore a LEFT JOIN funcionarios f ON f.cargo_id = a.id
GROUP BY a.id
ORDER BY a.nivel;
