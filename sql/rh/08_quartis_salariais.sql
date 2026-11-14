-- Distribuicao dos salarios atuais em quartis (NTILE) com tempo de casa em anos ate 2025-06-30 (strftime/julianday).
SELECT nome, valor, NTILE(4) OVER (ORDER BY valor) AS quartil,
       CAST((julianday('2025-06-30') - julianday(admissao)) / 365.25 AS INTEGER) AS anos_casa
FROM (
  SELECT f.nome, f.admissao, s.valor FROM funcionarios f JOIN salarios s ON s.funcionario_id = f.id
  WHERE s.vigencia_inicio = (SELECT MAX(vigencia_inicio) FROM salarios WHERE funcionario_id = f.id)
)
ORDER BY valor;
