-- Saldo de cada conta (contas sem lançamentos ficam com 0)
SELECT c.nome AS conta, COALESCE(SUM(l.valor), 0) AS saldo
FROM contas c
LEFT JOIN lancamentos l ON l.conta_id = c.id
GROUP BY c.id
ORDER BY c.id;
