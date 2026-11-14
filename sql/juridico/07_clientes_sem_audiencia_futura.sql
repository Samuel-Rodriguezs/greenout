-- Clientes com processo ativo mas sem nenhuma audiência marcada após 2025-06-15 (NOT EXISTS correlacionado).
SELECT c.nome,
       (SELECT COUNT(*) FROM processos p WHERE p.cliente_id = c.id AND p.status = 'ativo') AS ativos
FROM clientes c
WHERE EXISTS (SELECT 1 FROM processos p WHERE p.cliente_id = c.id AND p.status = 'ativo')
  AND NOT EXISTS (SELECT 1 FROM processos p JOIN audiencias a ON a.processo_id = p.id
                  WHERE p.cliente_id = c.id AND a.data > '2025-06-15')
ORDER BY c.nome;
