-- Top 2 imoveis de maior aluguel por bairro (ROW_NUMBER com PARTITION BY dentro de CTE).
WITH r AS (
  SELECT bairro, id, tipo, valor_aluguel,
         ROW_NUMBER() OVER (PARTITION BY bairro ORDER BY valor_aluguel DESC, id) AS pos
  FROM imoveis
)
SELECT bairro, id, tipo, valor_aluguel, pos FROM r WHERE pos <= 2 ORDER BY bairro, pos;
