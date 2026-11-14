-- Percentual de parcelas pagas com atraso ou em aberto por locatario (SUM de CASE / COUNT), apenas quem teve alguma.
SELECT l.nome, COUNT(*) AS parcelas,
       SUM(CASE WHEN julianday(COALESCE(g.pago_em,'2025-06-30')) > julianday(g.vencimento) THEN 1 ELSE 0 END) AS problemas,
       ROUND(100.0 * SUM(CASE WHEN julianday(COALESCE(g.pago_em,'2025-06-30')) > julianday(g.vencimento) THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct
FROM locatarios l
JOIN contratos c ON c.locatario_id = l.id
JOIN pagamentos g ON g.contrato_id = c.id
GROUP BY l.id
HAVING problemas > 0
ORDER BY pct DESC, l.nome;
