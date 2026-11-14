-- Situação do aluno: Aprovado (>= 7), Recuperação (>= 5) ou Reprovado
SELECT a.nome AS aluno,
       CASE
           WHEN AVG(n.nota) >= 7 THEN 'Aprovado'
           WHEN AVG(n.nota) >= 5 THEN 'Recuperação'
           ELSE 'Reprovado'
       END AS situacao
FROM alunos a
JOIN notas n ON n.aluno_id = a.id
GROUP BY a.id
ORDER BY a.nome;
