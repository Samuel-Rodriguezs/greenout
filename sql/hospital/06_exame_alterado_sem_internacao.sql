-- Pacientes com exame alterado que nunca foram internados (EXCEPT).
SELECT p.nome FROM pacientes p
JOIN consultas c ON c.paciente_id = p.id
JOIN exames e ON e.consulta_id = c.id
WHERE e.resultado = 'alterado'
EXCEPT
SELECT p.nome FROM pacientes p JOIN internacoes i ON i.paciente_id = p.id
ORDER BY 1;
