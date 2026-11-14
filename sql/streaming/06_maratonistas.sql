-- Usuários que assistiram todos os episódios de uma série (NOT EXISTS de episódio não visto + EXISTS de visualização).
SELECT u.nome, t.nome AS serie
FROM usuarios u CROSS JOIN titulos t
WHERE t.tipo = 'serie'
  AND EXISTS (SELECT 1 FROM visualizacoes v JOIN episodios e ON e.id = v.episodio_id
              WHERE v.usuario_id = u.id AND e.titulo_id = t.id)
  AND NOT EXISTS (SELECT 1 FROM episodios e
                  WHERE e.titulo_id = t.id
                    AND NOT EXISTS (SELECT 1 FROM visualizacoes v
                                    WHERE v.episodio_id = e.id AND v.usuario_id = u.id))
ORDER BY u.nome, t.nome;
