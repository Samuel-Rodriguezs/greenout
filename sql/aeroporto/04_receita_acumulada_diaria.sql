-- Receita diária (por dia de partida) e acumulada no período (CTE + SUM OVER + strftime).
WITH diaria AS (
  SELECT strftime('%Y-%m-%d', v.partida) AS dia, SUM(r.valor_pago) AS receita
  FROM reservas r JOIN voos v ON v.id = r.voo_id
  WHERE r.status = 'confirmada'
  GROUP BY dia
)
SELECT dia, receita, SUM(receita) OVER (ORDER BY dia) AS acumulada
FROM diaria ORDER BY dia;
