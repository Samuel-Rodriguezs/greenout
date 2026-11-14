-- Pratos mais caros que a media do proprio restaurante (subconsulta correlacionada) com unidades vendidas via COALESCE.
SELECT r.nome AS restaurante, pr.nome AS prato, pr.preco,
       COALESCE((SELECT SUM(i.qtd) FROM itens_pedido i WHERE i.prato_id = pr.id), 0) AS unidades
FROM pratos pr JOIN restaurantes r ON r.id = pr.restaurante_id
WHERE pr.preco > (SELECT AVG(x.preco) FROM pratos x WHERE x.restaurante_id = pr.restaurante_id)
ORDER BY r.nome, pr.preco DESC;
