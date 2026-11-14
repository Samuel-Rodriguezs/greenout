# histograma.awk - histograma ASCII a partir de linhas "rotulo valor".
# Uso: awk -v largura=20 -f histograma.awk dados.txt
#   largura  tamanho da maior barra (padrao 20)
# Cada barra tem round(valor/max*largura) caracteres '#'. Linhas malformadas
# (sem 2 campos ou valor nao numerico/negativo) sao ignoradas.
BEGIN { if (largura == "") largura = 20 }
NF == 2 && $2 ~ /^([0-9]+\.?[0-9]*|\.[0-9]+)$/ {
    n++; rot[n] = $1; val[n] = $2 + 0
    if (length($1) > lr) lr = length($1)
    if (val[n] > max) max = val[n]
}
END {
    for (i = 1; i <= n; i++) {
        t = (max > 0) ? int(val[i] / max * largura + 0.5) : 0
        barra = sprintf("%" t "s", ""); gsub(/ /, "#", barra)
        printf "%-" lr "s | %s %s\n", rot[i], barra, val[i]
    }
}
