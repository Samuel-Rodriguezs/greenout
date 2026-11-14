-- Maior despesa de cada categoria (ROW_NUMBER; desempate pela data mais antiga)
WITH numerado AS (
    SELECT c.nome AS categoria, l.descricao, -l.valor AS gasto,
           ROW_NUMBER() OVER (PARTITION BY c.id ORDER BY l.valor, l.data) AS rn
    FROM lancamentos l
    JOIN categorias c ON c.id = l.categoria_id
    WHERE l.valor < 0
)
SELECT categoria, descricao, gasto
FROM numerado
WHERE rn = 1
ORDER BY gasto DESC, categoria;
