-- SUM OVER: total acumulado da receita mensal (pedidos não cancelados)
WITH mensal AS (
    SELECT strftime('%Y-%m', p.data) AS mes,
           SUM(i.quantidade * i.preco_unitario) AS receita
    FROM pedidos p
    JOIN itens_pedido i ON i.pedido_id = p.id
    WHERE p.status <> 'cancelado'
    GROUP BY mes
)
SELECT mes, receita,
       SUM(receita) OVER (ORDER BY mes) AS acumulado
FROM mensal
ORDER BY mes;
