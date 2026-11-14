# estat_coluna.awk - soma, media, minimo e maximo de uma coluna numerica.
# Uso: awk -F, -v col=2 -f estat_coluna.awk arquivo.csv
#   col  numero da coluna (padrao 1); separador livre via -F.
# Linhas cuja coluna nao e numerica (cabecalhos, malformadas) sao ignoradas.
# Saida: n=<qtd> soma=<s> media=<m> min=<min> max=<max>  (zeros se nao houver dados)
BEGIN { if (col == "") col = 1 }
$col ~ /^[+-]?([0-9]+\.?[0-9]*|\.[0-9]+)$/ {
    v = $col + 0
    if (n == 0 || v < min) min = v
    if (n == 0 || v > max) max = v
    soma += v; n++
}
END {
    if (n == 0) { print "n=0 soma=0 media=0 min=0 max=0"; exit }
    printf "n=%d soma=%s media=%s min=%s max=%s\n", n, soma, soma / n, min, max
}
