-- Ranking do valor da causa dentro de cada área do direito (RANK + PARTITION BY), com o nome do cliente.
SELECT area, numero, cliente, valor_causa, posicao FROM (
  SELECT p.area, p.numero, c.nome AS cliente, p.valor_causa,
         RANK() OVER (PARTITION BY p.area ORDER BY p.valor_causa DESC) AS posicao
  FROM processos p JOIN clientes c ON c.id = p.cliente_id
)
ORDER BY area, posicao;
