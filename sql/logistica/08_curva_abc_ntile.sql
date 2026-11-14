-- Curva ABC por volume de saídas dividida em três faixas iguais com NTILE (LEFT JOIN + COALESCE para itens sem saída).
SELECT produto, saidas, CASE faixa WHEN 1 THEN 'A' WHEN 2 THEN 'B' ELSE 'C' END AS classe FROM (
  SELECT p.nome AS produto, COALESCE(SUM(m.qtd), 0) AS saidas,
         NTILE(3) OVER (ORDER BY COALESCE(SUM(m.qtd), 0) DESC, p.nome) AS faixa
  FROM produtos p
  LEFT JOIN lotes l ON l.produto_id = p.id
  LEFT JOIN movimentacoes m ON m.lote_id = l.id AND m.tipo = 'S'
  GROUP BY p.id
)
ORDER BY saidas DESC, produto;
