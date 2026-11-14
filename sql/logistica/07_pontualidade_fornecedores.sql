-- Pontualidade dos fornecedores nos pedidos recebidos: atrasos, percentual e prazo médio de entrega (AVG + julianday).
SELECT f.nome AS fornecedor, COUNT(*) AS pedidos,
       SUM(CASE WHEN pc.entrega > pc.previsto THEN 1 ELSE 0 END) AS atrasados,
       ROUND(100.0 * SUM(CASE WHEN pc.entrega > pc.previsto THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_atraso,
       ROUND(AVG(julianday(pc.entrega) - julianday(pc.data)), 1) AS prazo_medio_dias
FROM pedidos_compra pc
JOIN fornecedores f ON f.id = pc.fornecedor_id
WHERE pc.status = 'recebido'
GROUP BY f.id
ORDER BY pct_atraso DESC, f.nome;
