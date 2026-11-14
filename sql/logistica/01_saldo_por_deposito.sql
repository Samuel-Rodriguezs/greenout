-- Saldo de estoque por depósito e categoria (entradas menos saídas) e valor imobilizado ao custo (JOINs múltiplos + HAVING).
SELECT d.nome AS deposito, c.nome AS categoria,
       SUM(CASE WHEN m.tipo = 'E' THEN m.qtd ELSE -m.qtd END) AS saldo,
       ROUND(SUM(CASE WHEN m.tipo = 'E' THEN m.qtd ELSE -m.qtd END * p.custo), 2) AS valor
FROM movimentacoes m
JOIN lotes l ON l.id = m.lote_id
JOIN depositos d ON d.id = l.deposito_id
JOIN produtos p ON p.id = l.produto_id
JOIN categorias c ON c.id = p.categoria_id
GROUP BY d.id, c.id
HAVING saldo > 0
ORDER BY d.nome, c.nome;
