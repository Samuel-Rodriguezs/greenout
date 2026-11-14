-- Prazos pendentes que vencem em até 15 dias (ou já vencidos), classificados com CASE; referência 2025-06-15 (julianday).
SELECT p.numero, z.descricao, z.vencimento,
       CAST(julianday(z.vencimento) - julianday('2025-06-15') AS INTEGER) AS dias,
       CASE
         WHEN julianday(z.vencimento) < julianday('2025-06-15') THEN 'vencido'
         WHEN julianday(z.vencimento) - julianday('2025-06-15') <= 3 THEN 'urgente'
         ELSE 'próximo'
       END AS situacao
FROM prazos z
JOIN processos p ON p.id = z.processo_id
WHERE z.cumprido = 0
  AND julianday(z.vencimento) - julianday('2025-06-15') <= 15
ORDER BY dias, p.numero;
