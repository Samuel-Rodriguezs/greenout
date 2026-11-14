-- Artigo mais citado de cada área (top-1 por grupo com ROW_NUMBER; desempate pelo menor id).
SELECT area, titulo, citacoes FROM (
  SELECT ar.nome AS area, a.titulo, COUNT(c.citante_id) AS citacoes,
         ROW_NUMBER() OVER (PARTITION BY ar.id ORDER BY COUNT(c.citante_id) DESC, a.id) AS rn
  FROM artigos a
  JOIN areas ar ON ar.id = a.area_id
  LEFT JOIN citacoes c ON c.citado_id = a.id
  GROUP BY a.id
)
WHERE rn = 1
ORDER BY citacoes DESC, area;
