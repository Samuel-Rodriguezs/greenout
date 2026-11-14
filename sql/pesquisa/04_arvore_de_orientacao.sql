-- Árvore de orientação acadêmica (CTE recursiva): nível, caminho e total de descendentes de cada raiz.
WITH RECURSIVE arvore(id, nome, nivel, caminho) AS (
  SELECT id, nome, 0, nome FROM pesquisadores WHERE orientador_id IS NULL
  UNION ALL
  SELECT p.id, p.nome, t.nivel + 1, t.caminho || ' > ' || p.nome
  FROM pesquisadores p JOIN arvore t ON p.orientador_id = t.id
)
SELECT t.nome, t.nivel, t.caminho,
       (SELECT COUNT(*) FROM arvore d WHERE d.caminho LIKE t.caminho || ' > %') AS orientados
FROM arvore t
ORDER BY t.caminho;
