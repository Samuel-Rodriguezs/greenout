-- Faturamento dos pedidos entregues por restaurante: pedidos, itens vendidos e receita de pratos (JOIN de 4 tabelas, GROUP BY).
SELECT r.nome, COUNT(DISTINCT p.id) AS pedidos, SUM(i.qtd) AS itens, SUM(i.qtd * pr.preco) AS receita
FROM restaurantes r
JOIN pedidos p ON p.restaurante_id = r.id
JOIN itens_pedido i ON i.pedido_id = p.id
JOIN pratos pr ON pr.id = i.prato_id
WHERE p.status = 'entregue'
GROUP BY r.id
ORDER BY receita DESC;
