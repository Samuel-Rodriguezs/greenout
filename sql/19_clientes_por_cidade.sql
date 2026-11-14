-- COALESCE: clientes por cidade, rotulando cidade ausente
SELECT COALESCE(cidade, 'Não informada') AS cidade, COUNT(*) AS clientes
FROM clientes
GROUP BY COALESCE(cidade, 'Não informada')
ORDER BY clientes DESC, cidade;
