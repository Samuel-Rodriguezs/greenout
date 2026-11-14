-- Destinos alcançáveis a partir de CWB em até 2 trechos (CTE recursiva sem ciclos), com o menor nº de trechos.
WITH RECURSIVE alcance(destino, trechos, caminho) AS (
  SELECT DISTINCT destino, 1, origem || '>' || destino FROM voos WHERE origem = 'CWB'
  UNION
  SELECT v.destino, a.trechos + 1, a.caminho || '>' || v.destino
  FROM alcance a JOIN voos v ON v.origem = a.destino
  WHERE a.trechos < 2 AND instr(a.caminho, v.destino) = 0
)
SELECT destino, MIN(trechos) AS trechos FROM alcance GROUP BY destino ORDER BY trechos, destino;
