-- Pesquisadores sem financiamento vigente em 2025-06-15 (NOT EXISTS), separando quem já teve (EXISTS) de quem nunca teve.
SELECT p.nome, i.nome AS instituicao,
       CASE WHEN EXISTS (SELECT 1 FROM financiamentos f WHERE f.pesquisador_id = p.id)
            THEN 'financiamento encerrado' ELSE 'nunca financiado' END AS situacao
FROM pesquisadores p
JOIN instituicoes i ON i.id = p.instituicao_id
WHERE NOT EXISTS (SELECT 1 FROM financiamentos f
                  WHERE f.pesquisador_id = p.id AND f.inicio <= '2025-06-15' AND f.fim >= '2025-06-15')
ORDER BY situacao, p.nome;
