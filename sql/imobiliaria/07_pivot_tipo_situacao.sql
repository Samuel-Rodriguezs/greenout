-- Pivot manual: quantidade de parcelas por tipo de imovel e situacao (em dia, com atraso, em aberto).
SELECT i.tipo,
  SUM(CASE WHEN g.pago_em IS NOT NULL AND g.pago_em <= g.vencimento THEN 1 ELSE 0 END) AS em_dia,
  SUM(CASE WHEN g.pago_em IS NOT NULL AND g.pago_em > g.vencimento THEN 1 ELSE 0 END) AS com_atraso,
  SUM(CASE WHEN g.pago_em IS NULL THEN 1 ELSE 0 END) AS em_aberto
FROM pagamentos g
JOIN contratos c ON c.id = g.contrato_id
JOIN imoveis i ON i.id = c.imovel_id
GROUP BY i.tipo
ORDER BY i.tipo;
