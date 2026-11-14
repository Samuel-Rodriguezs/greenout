-- Saldo acumulado da conta corrente a cada lançamento (SUM OVER)
SELECT data, descricao, valor,
       SUM(valor) OVER (ORDER BY data, id) AS saldo
FROM lancamentos
WHERE conta_id = 1
ORDER BY data, id;
