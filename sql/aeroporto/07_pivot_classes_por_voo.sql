-- Pivot manual: reservas confirmadas por voo, uma coluna por classe tarifária (CASE).
SELECT v.codigo,
  SUM(CASE WHEN t.classe = 'economica'   THEN 1 ELSE 0 END) AS economica,
  SUM(CASE WHEN t.classe = 'executiva'   THEN 1 ELSE 0 END) AS executiva,
  SUM(CASE WHEN t.classe = 'promocional' THEN 1 ELSE 0 END) AS promocional
FROM reservas r
JOIN voos v ON v.id = r.voo_id
JOIN tarifas t ON t.id = r.tarifa_id
WHERE r.status = 'confirmada'
GROUP BY v.id
ORDER BY v.codigo;
