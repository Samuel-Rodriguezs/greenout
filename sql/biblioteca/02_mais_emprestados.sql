-- Os 3 livros mais emprestados (desempate por título)
SELECT l.titulo, COUNT(*) AS total
FROM emprestimos e
JOIN livros l ON l.id = e.livro_id
GROUP BY l.id
ORDER BY total DESC, l.titulo
LIMIT 3;
