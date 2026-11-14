-- Total gasto por mês (apenas despesas), usando strftime
SELECT strftime('%Y-%m', data) AS mes, -SUM(valor) AS gasto
FROM lancamentos
WHERE valor < 0
GROUP BY mes
ORDER BY mes;
