-- Honorários recebidos por mês de pagamento, com total acumulado e participação percentual (SUM OVER, strftime).
WITH mensal AS (
  SELECT strftime('%Y-%m', pago_em) AS mes, SUM(valor) AS recebido
  FROM parcelas WHERE pago_em IS NOT NULL
  GROUP BY mes
)
SELECT mes, recebido,
       SUM(recebido) OVER (ORDER BY mes) AS acumulado,
       ROUND(100.0 * recebido / SUM(recebido) OVER (), 1) AS percentual
FROM mensal
ORDER BY mes;
