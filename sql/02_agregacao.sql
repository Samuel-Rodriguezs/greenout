-- Média salarial e quantidade de funcionários por departamento
SELECT d.nome AS departamento,
       COUNT(f.id)  AS total,
       AVG(f.salario) AS media_salarial
FROM departamentos d
LEFT JOIN funcionarios f ON f.departamento_id = d.id
GROUP BY d.id
ORDER BY d.nome;
