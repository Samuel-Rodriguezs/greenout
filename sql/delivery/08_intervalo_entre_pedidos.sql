-- Dias entre pedidos consecutivos de cada cliente (LAG + julianday), apenas clientes recorrentes.
SELECT nome, data, dias_desde_anterior FROM (
  SELECT c.nome, substr(p.data_hora, 1, 10) AS data,
         CAST(julianday(substr(p.data_hora,1,10)) - julianday(LAG(substr(p.data_hora,1,10)) OVER (PARTITION BY c.id ORDER BY p.data_hora)) AS INTEGER) AS dias_desde_anterior
  FROM pedidos p JOIN clientes c ON c.id = p.cliente_id
)
WHERE dias_desde_anterior IS NOT NULL
ORDER BY nome, data;
