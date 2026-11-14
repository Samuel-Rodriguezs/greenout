# numerar.awk - numera linhas no formato "<numero><TAB><linha>".
# Uso: awk -v inicio=1 -v pular_vazias=0 -f numerar.awk arquivo
#   inicio        primeiro numero (padrao 1)
#   pular_vazias  se 1, linhas vazias sao impressas sem numero e nao contam
BEGIN { if (inicio == "") inicio = 1; atual = inicio }
{
    if (pular_vazias == 1 && $0 ~ /^[[:space:]]*$/) { print; next }
    printf "%d\t%s\n", atual++, $0
}
