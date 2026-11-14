-- Médicos com pelo menos 2 consultas realizadas, com total de consultas e receita (JOIN + GROUP BY + HAVING).
SELECT m.nome, COUNT(*) AS consultas, SUM(c.valor) AS receita
FROM medicos m
JOIN consultas c ON c.medico_id = m.id
WHERE c.status = 'realizada'
GROUP BY m.id
HAVING COUNT(*) >= 2
ORDER BY receita DESC, m.nome;
