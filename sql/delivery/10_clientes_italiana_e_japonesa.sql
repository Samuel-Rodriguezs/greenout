-- Clientes que pediram tanto de restaurante italiano quanto de japones (INTERSECT).
SELECT c.nome FROM clientes c JOIN pedidos p ON p.cliente_id = c.id JOIN restaurantes r ON r.id = p.restaurante_id
WHERE r.culinaria = 'italiana' AND p.status = 'entregue'
INTERSECT
SELECT c.nome FROM clientes c JOIN pedidos p ON p.cliente_id = c.id JOIN restaurantes r ON r.id = p.restaurante_id
WHERE r.culinaria = 'japonesa' AND p.status = 'entregue'
ORDER BY 1;
