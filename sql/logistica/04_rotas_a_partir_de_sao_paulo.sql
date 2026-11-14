-- Menor distância de CD São Paulo a cada depósito alcançável (CTE recursiva sobre o grafo de rotas, sem repetir nós).
WITH RECURSIVE caminhos(destino_id, saltos, km, trajeto) AS (
  SELECT r.destino_id, 1, r.km, '1>' || r.destino_id
  FROM rotas r WHERE r.origem_id = 1
  UNION ALL
  SELECT r.destino_id, c.saltos + 1, c.km + r.km, c.trajeto || '>' || r.destino_id
  FROM caminhos c JOIN rotas r ON r.origem_id = c.destino_id
  WHERE instr('>' || c.trajeto || '>', '>' || r.destino_id || '>') = 0
),
melhores AS (
  SELECT destino_id, saltos, km, trajeto,
         ROW_NUMBER() OVER (PARTITION BY destino_id ORDER BY km) AS rn
  FROM caminhos
)
SELECT d.nome AS destino, m.saltos, m.km, m.trajeto
FROM melhores m JOIN depositos d ON d.id = m.destino_id
WHERE m.rn = 1 AND m.destino_id <> 1
ORDER BY m.km;
