-- Artigos agregados pela área raiz da hierarquia (CTE recursiva sobe cada área até a raiz) com fator médio dos periódicos.
WITH RECURSIVE sobe(area_id, raiz_id) AS (
  SELECT id, id FROM areas WHERE pai_id IS NULL
  UNION ALL
  SELECT a.id, s.raiz_id FROM areas a JOIN sobe s ON a.pai_id = s.area_id
)
SELECT r.nome AS area_raiz, COUNT(*) AS artigos, ROUND(AVG(pe.fator), 2) AS fator_medio, MIN(a.ano) AS primeiro_ano
FROM artigos a
JOIN sobe s ON s.area_id = a.area_id
JOIN areas r ON r.id = s.raiz_id
JOIN periodicos pe ON pe.id = a.periodico_id
GROUP BY r.id
ORDER BY artigos DESC, r.nome;
