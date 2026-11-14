-- Horas extras (acima de 8h/dia) por funcionario, com valor estimado a 150% da hora normal (base 160h/mes) usando CASE.
SELECT f.nome, SUM(CASE WHEN p.horas > 8 THEN p.horas - 8 ELSE 0 END) AS horas_extras,
       ROUND(SUM(CASE WHEN p.horas > 8 THEN p.horas - 8 ELSE 0 END) * s.valor / 160 * 1.5, 2) AS valor_extra
FROM ponto p
JOIN funcionarios f ON f.id = p.funcionario_id
JOIN salarios s ON s.funcionario_id = f.id
WHERE s.vigencia_inicio = (SELECT MAX(vigencia_inicio) FROM salarios WHERE funcionario_id = f.id)
GROUP BY f.id
HAVING horas_extras > 0
ORDER BY horas_extras DESC, f.nome;
