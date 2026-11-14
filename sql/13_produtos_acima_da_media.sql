-- Subconsulta escalar: produtos com preço acima da média geral
SELECT nome, preco
FROM produtos
WHERE preco > (SELECT AVG(preco) FROM produtos)
ORDER BY preco DESC;
