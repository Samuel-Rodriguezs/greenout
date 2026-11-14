-- Advogados com pelo menos 2 processos ativos: quantidade e soma do valor das causas (JOIN + GROUP BY + HAVING).
SELECT a.nome, COUNT(*) AS processos, SUM(p.valor_causa) AS total_causas
FROM advogados a
JOIN processos p ON p.advogado_id = a.id
WHERE p.status = 'ativo'
GROUP BY a.id
HAVING COUNT(*) >= 2
ORDER BY total_causas DESC, a.nome;
