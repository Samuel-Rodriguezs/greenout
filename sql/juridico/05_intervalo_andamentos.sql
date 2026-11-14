-- Dias decorridos entre andamentos consecutivos de cada processo (LAG + julianday).
SELECT numero, tipo, data, dias FROM (
  SELECT p.numero, a.tipo, a.data,
         CAST(julianday(a.data) - julianday(LAG(a.data) OVER (PARTITION BY a.processo_id ORDER BY a.data)) AS INTEGER) AS dias
  FROM andamentos a JOIN processos p ON p.id = a.processo_id
)
WHERE dias IS NOT NULL
ORDER BY numero, data;
