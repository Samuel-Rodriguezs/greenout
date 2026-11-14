-- Reservas confirmadas pagas acima da média da própria tarifa (subconsulta correlacionada),
-- apenas de passageiros que nunca cancelaram uma reserva (NOT EXISTS).
SELECT p.nome, v.codigo, t.classe, r.valor_pago
FROM reservas r
JOIN passageiros p ON p.id = r.passageiro_id
JOIN voos v ON v.id = r.voo_id
JOIN tarifas t ON t.id = r.tarifa_id
WHERE r.status = 'confirmada'
  AND r.valor_pago > (SELECT AVG(r2.valor_pago) FROM reservas r2
                      WHERE r2.tarifa_id = r.tarifa_id AND r2.status = 'confirmada')
  AND NOT EXISTS (SELECT 1 FROM reservas r3
                  WHERE r3.passageiro_id = r.passageiro_id AND r3.status = 'cancelada')
ORDER BY r.valor_pago DESC, p.nome;
