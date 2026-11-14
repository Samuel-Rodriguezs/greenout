-- Hierarquia de sócios e associados com CTE recursiva: nível, caminho e nº de processos de cada advogado.
WITH RECURSIVE arvore(id, nome, nivel, caminho) AS (
  SELECT id, nome, 0, nome FROM advogados WHERE socio_id IS NULL
  UNION ALL
  SELECT a.id, a.nome, t.nivel + 1, t.caminho || ' > ' || a.nome
  FROM advogados a JOIN arvore t ON a.socio_id = t.id
)
SELECT t.nome, t.nivel, t.caminho,
       (SELECT COUNT(*) FROM processos p WHERE p.advogado_id = t.id) AS processos
FROM arvore t
ORDER BY t.caminho;
