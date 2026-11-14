-- Quantidade de alunos por situação em cada turma
WITH situacao AS (
    SELECT a.turma_id,
           CASE
               WHEN AVG(n.nota) >= 7 THEN 'Aprovado'
               WHEN AVG(n.nota) >= 5 THEN 'Recuperação'
               ELSE 'Reprovado'
           END AS s
    FROM alunos a
    JOIN notas n ON n.aluno_id = a.id
    GROUP BY a.id
)
SELECT t.nome AS turma,
       SUM(s = 'Aprovado') AS aprovados,
       SUM(s = 'Recuperação') AS recuperacao,
       SUM(s = 'Reprovado') AS reprovados
FROM situacao
JOIN turmas t ON t.id = situacao.turma_id
GROUP BY t.id
ORDER BY t.nome;
