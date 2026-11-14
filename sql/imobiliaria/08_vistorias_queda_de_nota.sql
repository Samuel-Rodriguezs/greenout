-- Ultima vistoria de cada imovel e queda de nota em relacao a anterior (LAG + ROW_NUMBER, subconsulta correlacionada para a contagem).
WITH v AS (
  SELECT imovel_id, data, tipo, nota,
         LAG(nota) OVER (PARTITION BY imovel_id ORDER BY data) AS nota_anterior,
         ROW_NUMBER() OVER (PARTITION BY imovel_id ORDER BY data DESC) AS rn
  FROM vistorias
)
SELECT imovel_id, data, tipo, nota, nota_anterior,
       (SELECT COUNT(*) FROM vistorias x WHERE x.imovel_id = v.imovel_id) AS total_vistorias
FROM v
WHERE rn = 1 AND nota_anterior IS NOT NULL AND nota < nota_anterior
ORDER BY nota - nota_anterior, imovel_id;
