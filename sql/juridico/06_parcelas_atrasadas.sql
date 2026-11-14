-- Parcelas de honorários em atraso em 2025-06-15: dias de atraso, multa (2% + 0,1% ao dia) e faixa de atraso.
SELECT c.nome AS cliente, pc.numero AS parcela, pc.vencimento,
       CAST(julianday('2025-06-15') - julianday(pc.vencimento) AS INTEGER) AS dias_atraso,
       ROUND(pc.valor * (0.02 + 0.001 * (julianday('2025-06-15') - julianday(pc.vencimento))), 2) AS multa,
       CASE
         WHEN julianday('2025-06-15') - julianday(pc.vencimento) > 60 THEN 'crítico'
         WHEN julianday('2025-06-15') - julianday(pc.vencimento) > 30 THEN 'alto'
         ELSE 'leve'
       END AS faixa
FROM parcelas pc
JOIN honorarios h ON h.id = pc.honorario_id
JOIN processos p ON p.id = h.processo_id
JOIN clientes c ON c.id = p.cliente_id
WHERE COALESCE(pc.pago_em, '') = '' AND pc.vencimento < '2025-06-15'
ORDER BY dias_atraso DESC, c.nome;
