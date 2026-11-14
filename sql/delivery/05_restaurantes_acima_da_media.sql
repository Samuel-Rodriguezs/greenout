-- Restaurantes com nota media acima da media geral das avaliacoes (subconsulta escalar + HAVING).
SELECT r.nome, COUNT(*) AS avaliacoes, ROUND(AVG(a.nota), 2) AS media
FROM restaurantes r
JOIN pedidos p ON p.restaurante_id = r.id
JOIN avaliacoes a ON a.pedido_id = p.id
GROUP BY r.id
HAVING AVG(a.nota) > (SELECT AVG(nota) FROM avaliacoes)
ORDER BY media DESC;
