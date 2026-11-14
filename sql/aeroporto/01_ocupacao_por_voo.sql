-- Taxa de ocupação (%) de cada voo: reservas confirmadas / capacidade da aeronave (JOIN múltiplo + LEFT JOIN).
SELECT v.codigo, a.modelo, COUNT(r.id) AS passageiros,
       ROUND(100.0 * COUNT(r.id) / a.capacidade, 2) AS ocupacao_pct
FROM voos v
JOIN aeronaves a ON a.id = v.aeronave_id
LEFT JOIN reservas r ON r.voo_id = v.id AND r.status = 'confirmada'
GROUP BY v.id
ORDER BY ocupacao_pct DESC, v.codigo;
