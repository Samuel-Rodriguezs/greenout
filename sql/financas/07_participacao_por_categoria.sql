-- Participação (%) de cada categoria no total de despesas
SELECT c.nome AS categoria, -SUM(l.valor) AS total,
       ROUND(100.0 * SUM(l.valor) / SUM(SUM(l.valor)) OVER (), 1) AS percentual
FROM lancamentos l
JOIN categorias c ON c.id = l.categoria_id
WHERE l.valor < 0
GROUP BY c.id
ORDER BY total DESC, c.nome;
