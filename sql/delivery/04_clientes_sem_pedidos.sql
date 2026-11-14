-- Clientes que nunca fizeram pedido entregue (EXCEPT entre todos os clientes e os que receberam pedidos).
SELECT nome FROM clientes
EXCEPT
SELECT c.nome FROM clientes c JOIN pedidos p ON p.cliente_id = c.id WHERE p.status = 'entregue'
ORDER BY nome;
