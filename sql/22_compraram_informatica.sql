-- EXISTS: clientes que já compraram algum produto de Informática
SELECT c.nome
FROM clientes c
WHERE EXISTS (
    SELECT 1
    FROM pedidos p
    JOIN itens_pedido i ON i.pedido_id = p.id
    JOIN produtos pr ON pr.id = i.produto_id
    WHERE p.cliente_id = c.id AND pr.categoria = 'Informática'
)
ORDER BY c.nome;
