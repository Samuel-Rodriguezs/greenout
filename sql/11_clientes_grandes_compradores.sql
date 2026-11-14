-- GROUP BY + HAVING: clientes com pelo menos R$ 500 em pedidos entregues
SELECT c.nome, SUM(i.quantidade * i.preco_unitario) AS total
FROM clientes c
JOIN pedidos p ON p.cliente_id = c.id
JOIN itens_pedido i ON i.pedido_id = p.id
WHERE p.status = 'entregue'
GROUP BY c.id, c.nome
HAVING SUM(i.quantidade * i.preco_unitario) >= 500
ORDER BY total DESC, c.nome;
