-- Gasto por programa de fidelidade; passageiros sem programa aparecem como 'sem programa' (COALESCE).
SELECT COALESCE(p.programa_fidelidade, 'sem programa') AS programa,
       COUNT(DISTINCT p.id) AS passageiros, SUM(r.valor_pago) AS gasto
FROM passageiros p JOIN reservas r ON r.passageiro_id = p.id
WHERE r.status = 'confirmada'
GROUP BY programa
ORDER BY gasto DESC;
