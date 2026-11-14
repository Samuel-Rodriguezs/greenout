-- Parcelas sem registro de pagamento entre 2025-01 e 2025-06: CTE recursiva gera as competencias e LEFT JOIN encontra as lacunas.
WITH RECURSIVE meses(competencia) AS (
  SELECT '2025-01'
  UNION ALL
  SELECT strftime('%Y-%m', competencia || '-01', '+1 month') FROM meses WHERE competencia < '2025-06'
)
SELECT c.id AS contrato, m.competencia
FROM contratos c
JOIN meses m ON m.competencia BETWEEN strftime('%Y-%m', c.inicio) AND strftime('%Y-%m', c.fim)
LEFT JOIN pagamentos g ON g.contrato_id = c.id AND g.competencia = m.competencia
WHERE g.id IS NULL
ORDER BY c.id, m.competencia;
