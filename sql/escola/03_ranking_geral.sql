-- Ranking geral por média com RANK (empates dividem a posição)
WITH medias AS (
    SELECT a.nome AS aluno, AVG(n.nota) AS media
    FROM alunos a
    JOIN notas n ON n.aluno_id = a.id
    GROUP BY a.id
)
SELECT aluno, media, RANK() OVER (ORDER BY media DESC) AS posicao
FROM medias
ORDER BY posicao, aluno;
