# tabela.awk - formata colunas em tabela com larguras automaticas.
# Uso: awk -F, -f tabela.awk dados.csv        (separador de entrada via -F)
# Colunas separadas por " | "; uma linha de "-" e "+" abaixo do cabecalho (1a linha).
# Linhas com menos colunas sao completadas com vazio.
{
    for (i = 1; i <= NF; i++) {
        c[NR, i] = $i
        if (length($i) > larg[i]) larg[i] = length($i)
    }
    if (NF > maxc) maxc = NF
}
END {
    for (r = 1; r <= NR; r++) {
        linha = ""
        for (i = 1; i <= maxc; i++)
            linha = linha (i > 1 ? " | " : "") sprintf("%-" larg[i] "s", c[r, i])
        sub(/ +$/, "", linha)
        print linha
        if (r == 1) {
            sep = ""
            for (i = 1; i <= maxc; i++) {
                traco = sprintf("%" larg[i] "s", ""); gsub(/ /, "-", traco)
                sep = sep (i > 1 ? "-+-" : "") traco
            }
            print sep
        }
    }
}
