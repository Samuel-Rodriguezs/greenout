-- Pares (usuário, título) que o usuário assistiu mas não avaliou (EXCEPT).
SELECT u.nome, t.nome AS titulo
FROM visualizacoes v
JOIN usuarios u ON u.id = v.usuario_id
JOIN episodios e ON e.id = v.episodio_id
JOIN titulos t ON t.id = e.titulo_id
EXCEPT
SELECT u.nome, t.nome
FROM avaliacoes a
JOIN usuarios u ON u.id = a.usuario_id
JOIN titulos t ON t.id = a.titulo_id
ORDER BY 1, 2;
