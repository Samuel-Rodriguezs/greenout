# soma_por_chave.awk - GROUP BY chave com SUM e COUNT, na ordem de primeira aparicao.
# Uso: awk -F, -v k=1 -v v=2 -f soma_por_chave.awk vendas.csv
#   k  coluna da chave (padrao 1); v  coluna do valor (padrao 2)
# Saida: chave,soma,contagem. Linhas com valor nao numerico ou sem chave sao ignoradas.
BEGIN { if (k == "") k = 1; if (v == "") v = 2; OFS = "," }
$k != "" && $v ~ /^[+-]?([0-9]+\.?[0-9]*|\.[0-9]+)$/ {
    if (!($k in soma)) ordem[++total] = $k
    soma[$k] += $v
    cont[$k]++
}
END { for (i = 1; i <= total; i++) print ordem[i], soma[ordem[i]], cont[ordem[i]] }
