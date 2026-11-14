-- Partes que são clientes do escritório atuando como adversárias (INTERSECT) e adversários externos (EXCEPT), unidos com UNION ALL.
SELECT nome, tipo FROM (
  SELECT nome, 'cliente como adversário' AS tipo FROM (
    SELECT nome FROM clientes
    INTERSECT
    SELECT pt.nome FROM partes pt
      JOIN processos p ON p.id = pt.processo_id
      JOIN clientes c ON c.id = p.cliente_id
    WHERE pt.nome <> c.nome
  )
  UNION ALL
  SELECT nome, 'adversário externo' FROM (
    SELECT pt.nome FROM partes pt
      JOIN processos p ON p.id = pt.processo_id
      JOIN clientes c ON c.id = p.cliente_id
    WHERE pt.nome <> c.nome
    EXCEPT
    SELECT nome FROM clientes
  )
)
ORDER BY tipo, nome;
