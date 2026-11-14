-- Funcionários com o nome do departamento (INNER JOIN)
SELECT f.nome AS funcionario, d.nome AS departamento
FROM funcionarios f
JOIN departamentos d ON d.id = f.departamento_id
ORDER BY f.nome;
