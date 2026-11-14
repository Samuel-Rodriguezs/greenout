# caixa_campo.awk - muda a caixa de um campo: upper, lower ou title.
# Uso: awk -F, -v OFS=, -v campo=2 -v modo=upper -f caixa_campo.awk dados.csv
# Linhas com menos campos que "campo" passam inalteradas. Parametros invalidos: status 1.
BEGIN {
    if (campo !~ /^[0-9]+$/ || campo < 1 || (modo != "upper" && modo != "lower" && modo != "title")) {
        print "erro: use -v campo=N -v modo=upper|lower|title" > "/dev/stderr"; erro = 1; exit 1
    }
}
campo <= NF {
    if (modo == "upper") $campo = toupper($campo)
    else if (modo == "lower") $campo = tolower($campo)
    else {
        s = tolower($campo); r = ""; ini = 1
        for (i = 1; i <= length(s); i++) {
            ch = substr(s, i, 1)
            r = r (ini ? toupper(ch) : ch)
            ini = (ch !~ /[[:alpha:]]/)
        }
        $campo = r
    }
}
{ print }
END { if (erro) exit 1 }
