-- Pivot manual de pedidos por turno (almoco ate 15h, jantar depois) para cada restaurante, usando strftime.
SELECT r.nome,
  SUM(CASE WHEN CAST(strftime('%H', p.data_hora) AS INTEGER) < 15 THEN 1 ELSE 0 END) AS almoco,
  SUM(CASE WHEN CAST(strftime('%H', p.data_hora) AS INTEGER) >= 15 THEN 1 ELSE 0 END) AS jantar
FROM restaurantes r JOIN pedidos p ON p.restaurante_id = r.id
GROUP BY r.id
ORDER BY r.nome;
