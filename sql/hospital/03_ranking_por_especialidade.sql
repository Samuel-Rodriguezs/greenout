-- Ranking de médicos por receita dentro da especialidade (RANK com PARTITION BY).
WITH receita AS (
  SELECT m.nome, m.especialidade, SUM(c.valor) AS total
  FROM medicos m JOIN consultas c ON c.medico_id = m.id
  WHERE c.status = 'realizada'
  GROUP BY m.id
)
SELECT especialidade, nome, total,
       RANK() OVER (PARTITION BY especialidade ORDER BY total DESC) AS posicao
FROM receita
ORDER BY especialidade, posicao, nome;
