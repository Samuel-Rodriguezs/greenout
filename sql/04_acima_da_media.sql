-- Funcionários que ganham acima da média geral
SELECT nome, salario
FROM funcionarios
WHERE salario > (SELECT AVG(salario) FROM funcionarios)
ORDER BY salario DESC;
