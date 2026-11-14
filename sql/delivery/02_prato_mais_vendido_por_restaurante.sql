-- Prato mais vendido (em unidades) de cada restaurante, top-1 por grupo com ROW_NUMBER.
WITH v AS (
  SELECT r.nome AS restaurante, pr.nome AS prato, SUM(i.qtd) AS unidades,
         ROW_NUMBER() OVER (PARTITION BY r.id ORDER BY SUM(i.qtd) DESC, pr.nome) AS pos
  FROM itens_pedido i
  JOIN pedidos p ON p.id = i.pedido_id AND p.status = 'entregue'
  JOIN pratos pr ON pr.id = i.prato_id
  JOIN restaurantes r ON r.id = pr.restaurante_id
  GROUP BY r.id, pr.id
)
SELECT restaurante, prato, unidades FROM v WHERE pos = 1 ORDER BY restaurante;
