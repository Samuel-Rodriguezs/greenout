-- Duração das internações; sem alta (saida NULL) conta até 2025-04-01 e aparece como 'em andamento' (COALESCE).
SELECT p.nome, i.motivo,
       COALESCE(i.saida, 'em andamento') AS saida,
       CAST(julianday(COALESCE(i.saida, '2025-04-01')) - julianday(i.entrada) AS INTEGER) AS dias
FROM internacoes i
JOIN pacientes p ON p.id = i.paciente_id
ORDER BY dias DESC, p.nome;
