-- Ranking de leitores por total de empréstimos (RANK permite empates)
SELECT u.nome AS usuario, COUNT(e.id) AS total,
       RANK() OVER (ORDER BY COUNT(e.id) DESC) AS posicao
FROM usuarios u
LEFT JOIN emprestimos e ON e.usuario_id = u.id
GROUP BY u.id
ORDER BY posicao, u.nome;
