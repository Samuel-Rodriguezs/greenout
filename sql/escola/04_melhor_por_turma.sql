-- Melhor aluno de cada turma (ROW_NUMBER; desempate por nome)
WITH medias AS (
    SELECT t.nome AS turma, a.nome AS aluno, AVG(n.nota) AS media
    FROM alunos a
    JOIN turmas t ON t.id = a.turma_id
    JOIN notas n ON n.aluno_id = a.id
    GROUP BY a.id
),
numerado AS (
    SELECT turma, aluno, media,
           ROW_NUMBER() OVER (PARTITION BY turma ORDER BY media DESC, aluno) AS rn
    FROM medias
)
SELECT turma, aluno, media FROM numerado WHERE rn = 1 ORDER BY turma;
