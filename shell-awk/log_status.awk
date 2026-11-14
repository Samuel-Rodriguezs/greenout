# log_status.awk - conta respostas HTTP por status em log no formato common/combined.
# Uso: awk -f log_status.awk access.log
# O status e o campo logo apos a requisicao entre aspas ("GET / HTTP/1.1" 200 512).
# Saida: "<status> <contagem>" ordenado por status. Linhas que nao casam sao contadas
# e reportadas em stderr ("malformadas: N").
{
    if (match($0, /" [1-5][0-9][0-9] /)) {
        cont[substr($0, RSTART + 2, 3)]++
    } else ruins++
}
END {
    for (s in cont) print s, cont[s] | "LC_ALL=C sort"
    close("LC_ALL=C sort")
    if (ruins) print "malformadas: " ruins > "/dev/stderr"
}
