-- Última consulta realizada de cada paciente (subconsulta correlacionada) e se já teve exame (EXISTS).
SELECT p.nome, c.data, m.nome AS medico,
       EXISTS (SELECT 1 FROM exames e WHERE e.consulta_id = c.id) AS teve_exame
FROM pacientes p
JOIN consultas c ON c.paciente_id = p.id
JOIN medicos m ON m.id = c.medico_id
WHERE c.status = 'realizada'
  AND c.data = (SELECT MAX(c2.data) FROM consultas c2
                WHERE c2.paciente_id = p.id AND c2.status = 'realizada')
ORDER BY p.nome;
