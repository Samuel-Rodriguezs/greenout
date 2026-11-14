-- Nota média por título (COALESCE para títulos sem avaliação) com ranking (RANK).
SELECT t.nome, ROUND(COALESCE(AVG(a.nota), 0), 2) AS media, COUNT(a.id) AS avaliacoes,
       RANK() OVER (ORDER BY COALESCE(AVG(a.nota), 0) DESC) AS posicao
FROM titulos t LEFT JOIN avaliacoes a ON a.titulo_id = t.id
GROUP BY t.id
ORDER BY posicao, t.nome;
