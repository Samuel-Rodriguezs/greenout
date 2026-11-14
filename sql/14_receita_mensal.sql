-- CTE: receita mensal (pedidos não cancelados)
WITH itens_validos AS (
    SELECT strftime('%Y-%m', p.data) AS mes,
           i.quantidade * i.preco_unitario AS valor
    FROM pedidos p
    JOIN itens_pedido i ON i.pedido_id = p.id
    WHERE p.status <> 'cancelado'
)
SELECT mes, SUM(valor) AS receita
FROM itens_validos
GROUP BY mes
ORDER BY mes;
