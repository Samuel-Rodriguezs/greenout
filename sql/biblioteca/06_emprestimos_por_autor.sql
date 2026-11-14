-- Total de empréstimos por autor
SELECT a.nome AS autor, COUNT(*) AS total
FROM emprestimos e
JOIN livros l ON l.id = e.livro_id
JOIN autores a ON a.id = l.autor_id
GROUP BY a.id
ORDER BY total DESC, a.nome;
