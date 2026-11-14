-- Pares de coautores com pelo menos 2 artigos em conjunto (auto-JOIN em autorias + GROUP BY/HAVING).
SELECT p1.nome AS autor_a, p2.nome AS autor_b, COUNT(*) AS artigos_juntos
FROM autorias a1
JOIN autorias a2 ON a2.artigo_id = a1.artigo_id AND a2.pesquisador_id > a1.pesquisador_id
JOIN pesquisadores p1 ON p1.id = a1.pesquisador_id
JOIN pesquisadores p2 ON p2.id = a2.pesquisador_id
GROUP BY a1.pesquisador_id, a2.pesquisador_id
HAVING COUNT(*) >= 2
ORDER BY artigos_juntos DESC, autor_a, autor_b;
