-- Alunos com média acima da média da própria turma
WITH medias AS (
    SELECT a.turma_id, a.nome AS aluno, AVG(n.nota) AS media
    FROM alunos a
    JOIN notas n ON n.aluno_id = a.id
    GROUP BY a.id
)
SELECT t.nome AS turma, m.aluno, ROUND(m.media, 2) AS media
FROM medias m
JOIN turmas t ON t.id = m.turma_id
WHERE m.media > (SELECT AVG(media) FROM medias x WHERE x.turma_id = m.turma_id)
ORDER BY t.nome, m.aluno;
