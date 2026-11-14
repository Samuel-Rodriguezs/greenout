-- Funcionarios com afastamento mas sem ferias em 2025 (EXISTS, NOT EXISTS) e funcionarios sem ferias nem afastamento (EXCEPT), unidos.
SELECT nome, 'afastado sem ferias' AS situacao FROM funcionarios f
WHERE EXISTS (SELECT 1 FROM afastamentos a WHERE a.funcionario_id = f.id)
  AND NOT EXISTS (SELECT 1 FROM ferias v WHERE v.funcionario_id = f.id)
UNION ALL
SELECT nome, 'sem ferias e sem afastamento' FROM (
  SELECT nome FROM funcionarios
  EXCEPT SELECT f.nome FROM funcionarios f JOIN ferias v ON v.funcionario_id = f.id
  EXCEPT SELECT f.nome FROM funcionarios f JOIN afastamentos a ON a.funcionario_id = f.id
)
ORDER BY nome;
