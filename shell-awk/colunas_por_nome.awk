# colunas_por_nome.awk - extrai colunas pelo nome no cabecalho (1a linha).
# Uso: awk -F, -v OFS=, -v cols="nome,idade" -f colunas_por_nome.awk dados.csv
# A ordem de saida segue a de "cols". Coluna inexistente: erro em stderr, status 1.
BEGIN { if (cols == "") { print "erro: informe -v cols=a,b" > "/dev/stderr"; erro = 1; exit 1 } }
NR == 1 {
    for (i = 1; i <= NF; i++) pos[$i] = i
    m = split(cols, nomes, ",")
    for (j = 1; j <= m; j++)
        if (!(nomes[j] in pos)) {
            print "erro: coluna inexistente: " nomes[j] > "/dev/stderr"
            erro = 1; exit 1
        }
}
{
    linha = ""
    for (j = 1; j <= m; j++) linha = linha (j > 1 ? OFS : "") $(pos[nomes[j]])
    print linha
}
END { if (erro) exit 1 }
