-- Folha atual por departamento: funcionarios, total e media salarial (JOIN multiplo + subconsulta correlacionada + GROUP BY/HAVING).
SELECT d.nome AS departamento, COUNT(*) AS funcionarios,
       SUM(s.valor) AS folha, ROUND(AVG(s.valor), 2) AS media
FROM departamentos d
JOIN funcionarios f ON f.departamento_id = d.id
JOIN salarios s ON s.funcionario_id = f.id
WHERE s.vigencia_inicio = (SELECT MAX(s2.vigencia_inicio) FROM salarios s2 WHERE s2.funcionario_id = f.id)
GROUP BY d.id
HAVING COUNT(*) >= 2
ORDER BY folha DESC;
