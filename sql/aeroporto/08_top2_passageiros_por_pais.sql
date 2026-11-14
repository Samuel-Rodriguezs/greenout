-- Top 2 passageiros que mais gastaram em cada país (ROW_NUMBER com PARTITION BY).
WITH gasto AS (
  SELECT p.pais, p.nome, SUM(r.valor_pago) AS total
  FROM passageiros p JOIN reservas r ON r.passageiro_id = p.id
  WHERE r.status = 'confirmada'
  GROUP BY p.id
), ranq AS (
  SELECT pais, nome, total,
         ROW_NUMBER() OVER (PARTITION BY pais ORDER BY total DESC, nome) AS pos
  FROM gasto
)
SELECT pais, nome, total, pos FROM ranq WHERE pos <= 2 ORDER BY pais, pos;
