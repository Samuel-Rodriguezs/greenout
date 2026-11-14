-- UNION: clientes com pedido cancelado ou pendente, com o motivo
SELECT c.nome, 'cancelado' AS motivo
FROM clientes c JOIN pedidos p ON p.cliente_id = c.id
WHERE p.status = 'cancelado'
UNION
SELECT c.nome, 'pendente' AS motivo
FROM clientes c JOIN pedidos p ON p.cliente_id = c.id
WHERE p.status = 'pendente'
ORDER BY nome, motivo;
