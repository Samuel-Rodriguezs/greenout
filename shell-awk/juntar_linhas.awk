# juntar_linhas.awk - junta N linhas consecutivas em uma (como paste -d).
# Uso: awk -v n=3 -v sep=, -f juntar_linhas.awk arquivo
#   n    linhas por grupo (padrao 2, inteiro >= 1)
#   sep  separador (padrao ",")
# O ultimo grupo pode ter menos de n linhas.
BEGIN {
    if (n == "") n = 2
    if (sep == "") sep = ","
    if (n !~ /^[0-9]+$/ || n < 1) { print "erro: n invalido" > "/dev/stderr"; erro = 1; exit 1 }
}
{
    acum = (c == 0) ? $0 : acum sep $0
    if (++c == n) { print acum; c = 0 }
}
END { if (erro) exit 1; if (c > 0) print acum }
