-- CASE: classifica cada pedido por faixa de valor
WITH totais AS (
    SELECT pedido_id, SUM(quantidade * preco_unitario) AS total
    FROM itens_pedido
    GROUP BY pedido_id
)
SELECT pedido_id, total,
       CASE
           WHEN total >= 2000 THEN 'alto'
           WHEN total >= 500  THEN 'medio'
           ELSE 'baixo'
       END AS faixa
FROM totais
ORDER BY pedido_id;
