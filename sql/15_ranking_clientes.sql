-- Função de janela RANK: ranking de clientes por receita (pedidos não cancelados)
WITH receita AS (
    SELECT c.nome, SUM(i.quantidade * i.preco_unitario) AS total
    FROM clientes c
    JOIN pedidos p ON p.cliente_id = c.id
    JOIN itens_pedido i ON i.pedido_id = p.id
    WHERE p.status <> 'cancelado'
    GROUP BY c.id, c.nome
)
SELECT RANK() OVER (ORDER BY total DESC) AS posicao, nome, total
FROM receita
ORDER BY posicao, nome;
