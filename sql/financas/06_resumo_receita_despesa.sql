-- Resumo geral com UNION: receitas, despesas e resultado
SELECT 1 AS ordem, 'Receita' AS tipo, SUM(valor) AS total FROM lancamentos WHERE valor > 0
UNION
SELECT 2, 'Despesa', -SUM(valor) FROM lancamentos WHERE valor < 0
UNION
SELECT 3, 'Resultado', SUM(valor) FROM lancamentos
ORDER BY ordem;
