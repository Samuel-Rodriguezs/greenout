-- Pivot manual: processos por área (linhas) e status (colunas), com valor total das causas ativas.
SELECT area,
       SUM(CASE WHEN status = 'ativo' THEN 1 ELSE 0 END) AS ativos,
       SUM(CASE WHEN status = 'arquivado' THEN 1 ELSE 0 END) AS arquivados,
       SUM(CASE WHEN status = 'encerrado' THEN 1 ELSE 0 END) AS encerrados,
       COALESCE(SUM(CASE WHEN status = 'ativo' THEN valor_causa END), 0) AS valor_ativo
FROM processos
GROUP BY area
ORDER BY area;
