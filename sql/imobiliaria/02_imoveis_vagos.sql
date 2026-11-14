-- Imoveis vagos em 2025-06-30: todos os imoveis menos os que tem contrato vigente (EXCEPT dentro de subconsulta).
SELECT i.id, i.tipo, i.bairro, i.valor_aluguel
FROM imoveis i
WHERE i.id IN (
  SELECT id FROM imoveis
  EXCEPT
  SELECT imovel_id FROM contratos WHERE '2025-06-30' BETWEEN inicio AND fim
)
ORDER BY i.id;
