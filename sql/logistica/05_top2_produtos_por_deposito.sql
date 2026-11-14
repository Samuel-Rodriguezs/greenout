-- Os 2 produtos com mais saídas em cada depósito (ROW_NUMBER + PARTITION BY, top-N por grupo).
SELECT deposito, produto, saidas, posicao FROM (
  SELECT d.nome AS deposito, p.nome AS produto, SUM(m.qtd) AS saidas,
         ROW_NUMBER() OVER (PARTITION BY d.id ORDER BY SUM(m.qtd) DESC, p.nome) AS posicao
  FROM movimentacoes m
  JOIN lotes l ON l.id = m.lote_id
  JOIN depositos d ON d.id = l.deposito_id
  JOIN produtos p ON p.id = l.produto_id
  WHERE m.tipo = 'S'
  GROUP BY d.id, p.id
)
WHERE posicao <= 2
ORDER BY deposito, posicao;
