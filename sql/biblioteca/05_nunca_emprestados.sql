-- Livros que nunca foram emprestados
SELECT l.titulo
FROM livros l
WHERE NOT EXISTS (SELECT 1 FROM emprestimos e WHERE e.livro_id = l.id)
ORDER BY l.titulo;
