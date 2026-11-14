-- LEFT JOIN: quantidade de pedidos por cliente, incluindo quem nunca comprou
SELECT c.nome, COUNT(p.id) AS pedidos
FROM clientes c
LEFT JOIN pedidos p ON p.cliente_id = c.id
GROUP BY c.id, c.nome
ORDER BY pedidos DESC, c.nome;
