# top_palavras.awk - frequencia de palavras (top-N), sem diferenciar maiusculas.
# Uso: awk -v n=5 -f top_palavras.awk texto.txt
#   n  quantidade de palavras exibidas (padrao 10)
# Saida: "<contagem> <palavra>", ordenada por contagem desc e palavra asc.
BEGIN { if (n == "") n = 10 }
{
    linha = tolower($0)
    gsub(/[^[:alpha:]]+/, " ", linha)
    k = split(linha, p, " ")
    for (i = 1; i <= k; i++) freq[p[i]]++
}
END {
    cmd = "LC_ALL=C sort -k1,1nr -k2,2 | head -n " n
    for (w in freq) print freq[w], w | cmd
    close(cmd)
}
