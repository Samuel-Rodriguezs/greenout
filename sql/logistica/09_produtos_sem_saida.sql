-- Produtos estocados que nunca tiveram saída (EXCEPT) e seu capital parado, via subconsulta correlacionada.
SELECT p.nome,
       (SELECT SUM(CASE WHEN m.tipo = 'E' THEN m.qtd ELSE -m.qtd END)
        FROM movimentacoes m JOIN lotes l ON l.id = m.lote_id WHERE l.produto_id = p.id) AS saldo,
       ROUND(p.custo * (SELECT SUM(CASE WHEN m.tipo = 'E' THEN m.qtd ELSE -m.qtd END)
        FROM movimentacoes m JOIN lotes l ON l.id = m.lote_id WHERE l.produto_id = p.id), 2) AS capital_parado
FROM produtos p
WHERE p.id IN (
  SELECT produto_id FROM lotes
  EXCEPT
  SELECT l.produto_id FROM movimentacoes m JOIN lotes l ON l.id = m.lote_id WHERE m.tipo = 'S'
)
ORDER BY p.nome;
