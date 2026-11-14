# tabuada.awk - gera a tabuada de um numero.
# Uso: awk -v n=7 -v ate=10 -f tabuada.awk </dev/null     (ate padrao 10)
# Saida: "7 x 1 = 7". n e ate devem ser inteiros nao negativos, senao status 1.
BEGIN {
    if (ate == "") ate = 10
    if (n !~ /^[0-9]+$/ || ate !~ /^[0-9]+$/) {
        print "erro: informe -v n=<inteiro> [-v ate=<inteiro>]" > "/dev/stderr"; exit 1
    }
    for (i = 1; i <= ate; i++) printf "%d x %d = %d\n", n, i, n * i
}
