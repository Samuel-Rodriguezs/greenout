-- Receita diaria de pratos (pedidos entregues), acumulada e percentual do total (SUM OVER, strftime).
WITH dia AS (
  SELECT substr(p.data_hora, 1, 10) AS data, SUM(i.qtd * pr.preco) AS receita
  FROM pedidos p JOIN itens_pedido i ON i.pedido_id = p.id JOIN pratos pr ON pr.id = i.prato_id
  WHERE p.status = 'entregue'
  GROUP BY data
)
SELECT data, receita,
       SUM(receita) OVER (ORDER BY data) AS acumulada,
       ROUND(100.0 * receita / SUM(receita) OVER (), 1) AS pct_total
FROM dia ORDER BY data;
