-- Pivot manual: dias de afastamento por tipo e funcionario; afastamentos em aberto contam ate 2025-06-30 (COALESCE + julianday).
SELECT f.nome,
  CAST(SUM(CASE WHEN a.tipo = 'licenca medica' THEN julianday(COALESCE(a.fim,'2025-06-30')) - julianday(a.inicio) + 1 ELSE 0 END) AS INTEGER) AS medica,
  CAST(SUM(CASE WHEN a.tipo = 'licenca maternidade' THEN julianday(COALESCE(a.fim,'2025-06-30')) - julianday(a.inicio) + 1 ELSE 0 END) AS INTEGER) AS maternidade,
  CAST(SUM(CASE WHEN a.tipo = 'treinamento' THEN julianday(COALESCE(a.fim,'2025-06-30')) - julianday(a.inicio) + 1 ELSE 0 END) AS INTEGER) AS treinamento
FROM funcionarios f JOIN afastamentos a ON a.funcionario_id = f.id
GROUP BY f.id
ORDER BY f.nome;
