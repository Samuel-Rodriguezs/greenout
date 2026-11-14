-- Datas: dias entre o cadastro e o primeiro pedido de cada cliente
SELECT c.nome,
       CAST(julianday(MIN(p.data)) - julianday(c.criado_em) AS INTEGER) AS dias
FROM clientes c
JOIN pedidos p ON p.cliente_id = c.id
GROUP BY c.id, c.nome, c.criado_em
ORDER BY dias, c.nome;
