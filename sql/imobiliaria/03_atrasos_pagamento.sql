-- Pagamentos em atraso: dias entre vencimento e pagamento (ou ate 2025-06-30 se em aberto), com CASE e COALESCE (julianday).
SELECT l.nome, g.competencia,
       CAST(julianday(COALESCE(g.pago_em, '2025-06-30')) - julianday(g.vencimento) AS INTEGER) AS dias_atraso,
       CASE WHEN g.pago_em IS NULL THEN 'em aberto' ELSE 'pago com atraso' END AS situacao
FROM pagamentos g
JOIN contratos c ON c.id = g.contrato_id
JOIN locatarios l ON l.id = c.locatario_id
WHERE julianday(COALESCE(g.pago_em, '2025-06-30')) > julianday(g.vencimento)
ORDER BY dias_atraso DESC, l.nome, g.competencia;
