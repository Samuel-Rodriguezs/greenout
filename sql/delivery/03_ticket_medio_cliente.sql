-- Ticket medio por cliente (itens + taxa) e perfil via CASE; CTE soma o valor de cada pedido entregue.
WITH valor AS (
  SELECT p.id, p.cliente_id, p.taxa_entrega + SUM(i.qtd * pr.preco) AS total
  FROM pedidos p
  JOIN itens_pedido i ON i.pedido_id = p.id
  JOIN pratos pr ON pr.id = i.prato_id
  WHERE p.status = 'entregue'
  GROUP BY p.id
)
SELECT c.nome, COUNT(*) AS pedidos, ROUND(AVG(v.total), 2) AS ticket_medio,
       CASE WHEN AVG(v.total) >= 100 THEN 'alto' WHEN AVG(v.total) >= 70 THEN 'medio' ELSE 'baixo' END AS perfil
FROM clientes c JOIN valor v ON v.cliente_id = c.id
GROUP BY c.id
ORDER BY ticket_medio DESC;
