-- Média de dias com o livro por usuário (apenas empréstimos devolvidos)
SELECT u.nome AS usuario,
       ROUND(AVG(julianday(e.data_devolucao) - julianday(e.data_emprestimo)), 1) AS media_dias
FROM emprestimos e
JOIN usuarios u ON u.id = e.usuario_id
WHERE e.data_devolucao IS NOT NULL
GROUP BY u.id
ORDER BY media_dias DESC;
