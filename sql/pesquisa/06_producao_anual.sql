-- Produção anual de artigos com variação em relação ao ano anterior (LAG) e ao primeiro ano (FIRST_VALUE).
SELECT ano, artigos,
       LAG(artigos) OVER (ORDER BY ano) AS anterior,
       artigos - LAG(artigos) OVER (ORDER BY ano) AS variacao,
       FIRST_VALUE(artigos) OVER (ORDER BY ano) AS primeiro_ano
FROM (SELECT ano, COUNT(*) AS artigos FROM artigos GROUP BY ano)
ORDER BY ano;
