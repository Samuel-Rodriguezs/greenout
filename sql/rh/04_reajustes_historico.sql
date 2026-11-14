-- Reajustes salariais: percentual de aumento entre salarios consecutivos (LAG).
SELECT nome, vigencia_inicio, valor, anterior,
       ROUND((valor - anterior) * 100.0 / anterior, 1) AS pct
FROM (
  SELECT f.nome, s.vigencia_inicio, s.valor,
         LAG(s.valor) OVER (PARTITION BY s.funcionario_id ORDER BY s.vigencia_inicio) AS anterior
  FROM salarios s JOIN funcionarios f ON f.id = s.funcionario_id
)
WHERE anterior IS NOT NULL
ORDER BY pct DESC, nome;
