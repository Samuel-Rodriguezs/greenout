-- Pivot manual: saídas por depósito (linhas) nos meses de março a junho de 2025 (colunas), com total (strftime + CASE).
SELECT d.nome AS deposito,
       SUM(CASE WHEN strftime('%m', m.data) = '03' THEN m.qtd ELSE 0 END) AS mar,
       SUM(CASE WHEN strftime('%m', m.data) = '04' THEN m.qtd ELSE 0 END) AS abr,
       SUM(CASE WHEN strftime('%m', m.data) = '05' THEN m.qtd ELSE 0 END) AS mai,
       SUM(CASE WHEN strftime('%m', m.data) = '06' THEN m.qtd ELSE 0 END) AS jun,
       SUM(m.qtd) AS total
FROM depositos d
JOIN lotes l ON l.deposito_id = d.id
JOIN movimentacoes m ON m.lote_id = l.id
WHERE m.tipo = 'S' AND m.data >= '2025-03-01'
GROUP BY d.id
ORDER BY total DESC, d.nome;
