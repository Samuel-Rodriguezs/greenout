-- Periódicos com pelo menos 2 artigos: quantidade, total de citações recebidas e média por artigo (JOIN + GROUP BY + HAVING).
SELECT p.nome AS periodico, COUNT(DISTINCT a.id) AS artigos, COUNT(c.citante_id) AS citacoes,
       ROUND(1.0 * COUNT(c.citante_id) / COUNT(DISTINCT a.id), 2) AS media
FROM periodicos p
JOIN artigos a ON a.periodico_id = p.id
LEFT JOIN citacoes c ON c.citado_id = a.id
GROUP BY p.id
HAVING COUNT(DISTINCT a.id) >= 2
ORDER BY citacoes DESC, p.nome;
