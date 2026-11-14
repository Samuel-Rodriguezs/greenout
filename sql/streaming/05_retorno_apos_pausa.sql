-- Usuários que voltaram a assistir após 7 dias ou mais de pausa (LAG + julianday).
WITH h AS (
  SELECT u.nome, v.data,
         LAG(v.data) OVER (PARTITION BY v.usuario_id ORDER BY v.data, v.id) AS anterior
  FROM visualizacoes v JOIN usuarios u ON u.id = v.usuario_id
)
SELECT nome, data, CAST(julianday(data) - julianday(anterior) AS INTEGER) AS dias_pausa
FROM h
WHERE anterior IS NOT NULL AND julianday(data) - julianday(anterior) >= 7
ORDER BY nome, data;
