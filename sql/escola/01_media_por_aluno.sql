-- Média de cada aluno, da maior para a menor
SELECT a.nome AS aluno, ROUND(AVG(n.nota), 2) AS media
FROM alunos a
JOIN notas n ON n.aluno_id = a.id
GROUP BY a.id
ORDER BY media DESC, a.nome;
