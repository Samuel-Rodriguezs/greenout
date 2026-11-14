-- Extrato do CD São Paulo: saldo corrente de cada lote após cada movimentação (SUM OVER com frame acumulado).
SELECT l.codigo, m.data, m.tipo, m.qtd,
       SUM(CASE WHEN m.tipo = 'E' THEN m.qtd ELSE -m.qtd END)
         OVER (PARTITION BY m.lote_id ORDER BY m.data, m.id) AS saldo
FROM movimentacoes m
JOIN lotes l ON l.id = m.lote_id
WHERE l.deposito_id = 1
ORDER BY l.codigo, m.data, m.id;
