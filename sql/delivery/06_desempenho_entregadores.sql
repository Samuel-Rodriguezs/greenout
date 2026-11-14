-- Desempenho dos entregadores: entregas, tempo medio em minutos (julianday) e ranking do mais rapido (RANK).
SELECT e.nome, COUNT(*) AS entregas,
       ROUND(AVG((julianday(p.entregue_em) - julianday(p.data_hora)) * 1440), 1) AS minutos_medios,
       RANK() OVER (ORDER BY ROUND(AVG((julianday(p.entregue_em) - julianday(p.data_hora)) * 1440), 1)) AS ranking
FROM entregadores e JOIN pedidos p ON p.entregador_id = e.id
WHERE p.entregue_em IS NOT NULL
GROUP BY e.id
ORDER BY ranking, e.nome;
