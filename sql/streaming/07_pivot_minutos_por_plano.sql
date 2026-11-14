-- Pivot manual: minutos assistidos por plano, com uma coluna por mês (strftime + CASE).
SELECT u.plano,
  SUM(CASE WHEN strftime('%m', v.data) = '01' THEN v.minutos ELSE 0 END) AS jan,
  SUM(CASE WHEN strftime('%m', v.data) = '02' THEN v.minutos ELSE 0 END) AS fev,
  SUM(CASE WHEN strftime('%m', v.data) = '03' THEN v.minutos ELSE 0 END) AS mar
FROM visualizacoes v JOIN usuarios u ON u.id = v.usuario_id
GROUP BY u.plano
ORDER BY u.plano;
