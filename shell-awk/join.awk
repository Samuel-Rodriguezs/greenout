# join.awk - inner join de dois arquivos pela primeira coluna.
# Uso: awk -F, -f join.awk esquerda.csv direita.csv
# Carrega o 1o arquivo em memoria e, para cada linha do 2o com chave presente,
# imprime: chave,<resto da esquerda>,<resto da direita>. Chaves sem par sao descartadas.
# (Usa FILENAME == ARGV[1] em vez de NR == FNR para funcionar com 1o arquivo vazio.)
BEGIN { OFS = FS }
function resto(   s, i) {
    s = ""
    for (i = 2; i <= NF; i++) s = s (i > 2 ? OFS : "") $i
    return s
}
FILENAME == ARGV[1] { if (NF >= 1 && $1 != "") esq[$1] = resto(); next }
NF >= 1 && ($1 in esq) { print $1, esq[$1], resto() }
