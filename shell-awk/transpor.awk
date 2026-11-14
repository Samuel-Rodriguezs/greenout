# transpor.awk - transposicao de matriz (linhas viram colunas).
# Uso: awk -f transpor.awk matriz.txt           (campos separados por espaco)
#      awk -F, -v OFS=, -f transpor.awk m.csv
# Linhas com menos campos que a maior sao completadas com "-".
{
    for (i = 1; i <= NF; i++) m[NR, i] = $i
    if (NF > maxc) maxc = NF
}
END {
    for (j = 1; j <= maxc; j++) {
        linha = ""
        for (i = 1; i <= NR; i++) {
            c = ((i, j) in m) ? m[i, j] : "-"
            linha = linha (i > 1 ? OFS : "") c
        }
        print linha
    }
}
