-- Cópias disponíveis de cada livro (cópias menos empréstimos em aberto)
SELECT l.titulo, l.copias - COUNT(e.id) AS disponiveis
FROM livros l
LEFT JOIN emprestimos e ON e.livro_id = l.id AND e.data_devolucao IS NULL
GROUP BY l.id
ORDER BY l.titulo;
