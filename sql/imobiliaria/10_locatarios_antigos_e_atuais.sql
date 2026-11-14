-- Locatarios que ja tiveram contrato encerrado e tambem tem contrato vigente em 2025-06-30 (INTERSECT).
SELECT l.nome FROM locatarios l JOIN contratos c ON c.locatario_id = l.id WHERE c.fim < '2025-06-30'
INTERSECT
SELECT l.nome FROM locatarios l JOIN contratos c ON c.locatario_id = l.id WHERE '2025-06-30' BETWEEN c.inicio AND c.fim
ORDER BY 1;
