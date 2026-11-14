-- Minutos assistidos por usuário e quantidade de títulos distintos; só quem passou de 100 min (JOIN múltiplo + HAVING).
SELECT u.nome, SUM(v.minutos) AS minutos, COUNT(DISTINCT e.titulo_id) AS titulos
FROM usuarios u
JOIN visualizacoes v ON v.usuario_id = u.id
JOIN episodios e ON e.id = v.episodio_id
GROUP BY u.id
HAVING SUM(v.minutos) > 100
ORDER BY minutos DESC, u.nome;
