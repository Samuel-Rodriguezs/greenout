-- Recebimento por mes de pagamento efetivo e variacao em relacao ao mes anterior (strftime + LAG).
WITH m AS (
  SELECT strftime('%Y-%m', pago_em) AS mes, SUM(valor) AS total
  FROM pagamentos WHERE pago_em IS NOT NULL GROUP BY mes
)
SELECT mes, total, LAG(total) OVER (ORDER BY mes) AS anterior,
       total - LAG(total) OVER (ORDER BY mes) AS variacao
FROM m ORDER BY mes;
