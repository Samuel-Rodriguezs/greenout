-- Calendário de 10 a 16/03/2024 (CTE recursiva) com o gasto de cada dia
WITH RECURSIVE dias(dia) AS (
    SELECT '2024-03-10'
    UNION ALL
    SELECT date(dia, '+1 day') FROM dias WHERE dia < '2024-03-16'
)
SELECT d.dia, COALESCE(-SUM(l.valor), 0) AS gasto
FROM dias d
LEFT JOIN lancamentos l ON l.data = d.dia AND l.valor < 0
GROUP BY d.dia
ORDER BY d.dia;
