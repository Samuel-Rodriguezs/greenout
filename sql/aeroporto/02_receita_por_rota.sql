-- Receita por rota (origem-destino) com reservas confirmadas; só rotas com receita >= 1000 (GROUP BY + HAVING).
SELECT v.origem || '-' || v.destino AS rota, COUNT(*) AS reservas, SUM(r.valor_pago) AS receita
FROM reservas r JOIN voos v ON v.id = r.voo_id
WHERE r.status = 'confirmada'
GROUP BY v.origem, v.destino
HAVING SUM(r.valor_pago) >= 1000
ORDER BY receita DESC, rota;
