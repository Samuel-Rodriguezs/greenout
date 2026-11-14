-- Hierarquia de chefia dos médicos com CTE recursiva: nível e caminho a partir da chefia máxima.
WITH RECURSIVE arvore(id, nome, nivel, caminho) AS (
  SELECT id, nome, 0, nome FROM medicos WHERE chefe_id IS NULL
  UNION ALL
  SELECT m.id, m.nome, a.nivel + 1, a.caminho || ' > ' || m.nome
  FROM medicos m JOIN arvore a ON m.chefe_id = a.id
)
SELECT nome, nivel, caminho FROM arvore ORDER BY caminho;
