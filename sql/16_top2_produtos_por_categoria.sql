-- ROW_NUMBER + top-N por grupo: 2 produtos de maior receita em cada categoria
WITH receita AS (
    SELECT pr.categoria, pr.nome, SUM(i.quantidade * i.preco_unitario) AS total
    FROM produtos pr
    JOIN itens_pedido i ON i.produto_id = pr.id
    JOIN pedidos p ON p.id = i.pedido_id
    WHERE p.status <> 'cancelado'
    GROUP BY pr.id, pr.categoria, pr.nome
),
numerado AS (
    SELECT categoria, nome, total,
           ROW_NUMBER() OVER (PARTITION BY categoria ORDER BY total DESC, nome) AS rn
    FROM receita
)
SELECT categoria, nome, total
FROM numerado
WHERE rn <= 2
ORDER BY categoria, rn;
