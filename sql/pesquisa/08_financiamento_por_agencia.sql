-- Financiamento por agência: total, percentual do total geral (SUM OVER) e quantos projetos estão vigentes em 2025-06-15.
SELECT agencia, SUM(valor) AS total,
       ROUND(100.0 * SUM(valor) / SUM(SUM(valor)) OVER (), 1) AS percentual,
       SUM(CASE WHEN inicio <= '2025-06-15' AND fim >= '2025-06-15' THEN 1 ELSE 0 END) AS vigentes,
       CAST(AVG(julianday(fim) - julianday(inicio)) / 30.44 AS INTEGER) AS duracao_media_meses
FROM financiamentos
GROUP BY agencia
ORDER BY total DESC;
