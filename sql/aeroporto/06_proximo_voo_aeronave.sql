-- Próximo voo de cada aeronave e horas de solo entre eles (LEAD + julianday); último voo fica de fora.
WITH seq AS (
  SELECT a.modelo, v.codigo, v.partida,
         LEAD(v.codigo)  OVER (PARTITION BY v.aeronave_id ORDER BY v.partida) AS proximo,
         LEAD(v.partida) OVER (PARTITION BY v.aeronave_id ORDER BY v.partida) AS prox_partida
  FROM voos v JOIN aeronaves a ON a.id = v.aeronave_id
)
SELECT modelo, codigo, proximo,
       ROUND((julianday(prox_partida) - julianday(partida)) * 24, 1) AS horas
FROM seq WHERE proximo IS NOT NULL
ORDER BY modelo, partida;
