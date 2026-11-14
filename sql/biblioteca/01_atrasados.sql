-- Empréstimos em aberto e atrasados em 2024-03-31, com dias de atraso
SELECT u.nome AS usuario, l.titulo,
       CAST(julianday('2024-03-31') - julianday(e.data_prevista) AS INTEGER) AS dias_atraso
FROM emprestimos e
JOIN usuarios u ON u.id = e.usuario_id
JOIN livros l ON l.id = e.livro_id
WHERE e.data_devolucao IS NULL AND e.data_prevista < '2024-03-31'
ORDER BY dias_atraso DESC;
