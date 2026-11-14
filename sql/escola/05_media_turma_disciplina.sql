-- Média de cada disciplina em cada turma
SELECT t.nome AS turma, d.nome AS disciplina, ROUND(AVG(n.nota), 2) AS media
FROM notas n
JOIN alunos a ON a.id = n.aluno_id
JOIN turmas t ON t.id = a.turma_id
JOIN disciplinas d ON d.id = n.disciplina_id
GROUP BY t.id, d.id
ORDER BY t.nome, d.nome;
