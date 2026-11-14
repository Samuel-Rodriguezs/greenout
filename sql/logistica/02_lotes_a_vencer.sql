-- Lotes com saldo que vencem em até 60 dias de 2025-06-15 (ou já vencidos), com faixa de risco (CTE + julianday + CASE).
WITH saldos AS (
  SELECT lote_id, SUM(CASE WHEN tipo = 'E' THEN qtd ELSE -qtd END) AS saldo
  FROM movimentacoes GROUP BY lote_id
)
SELECT l.codigo, p.nome AS produto, d.nome AS deposito, s.saldo, l.validade,
       CAST(julianday(l.validade) - julianday('2025-06-15') AS INTEGER) AS dias,
       CASE
         WHEN julianday(l.validade) < julianday('2025-06-15') THEN 'vencido'
         WHEN julianday(l.validade) - julianday('2025-06-15') <= 15 THEN 'crítico'
         ELSE 'atenção'
       END AS faixa
FROM lotes l
JOIN saldos s ON s.lote_id = l.id
JOIN produtos p ON p.id = l.produto_id
JOIN depositos d ON d.id = l.deposito_id
WHERE s.saldo > 0 AND julianday(l.validade) - julianday('2025-06-15') <= 60
ORDER BY dias;
