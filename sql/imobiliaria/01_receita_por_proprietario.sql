-- Receita recebida por proprietario (so pagamentos efetivados) com numero de imoveis com receita (JOIN de 4 tabelas, GROUP BY, HAVING).
SELECT p.nome, COUNT(DISTINCT i.id) AS imoveis, SUM(g.valor) AS recebido
FROM proprietarios p
JOIN imoveis i ON i.proprietario_id = p.id
JOIN contratos c ON c.imovel_id = i.id
JOIN pagamentos g ON g.contrato_id = c.id
WHERE g.pago_em IS NOT NULL
GROUP BY p.id
HAVING SUM(g.valor) > 5000
ORDER BY recebido DESC;
