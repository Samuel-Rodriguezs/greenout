# csv2tsv.awk - converte CSV (campos entre aspas, "" como aspas escapadas) em TSV.
# Uso: awk -f csv2tsv.awk entrada.csv > saida.tsv
# Virgulas dentro de aspas sao preservadas; tabs dentro de campos viram espaco.
# Aspas nao fechadas consomem o resto da linha como parte do campo.
{
    saida = ""; campo = ""; q = 0
    n = length($0)
    for (i = 1; i <= n; i++) {
        c = substr($0, i, 1)
        if (q) {
            if (c == "\"") {
                if (substr($0, i + 1, 1) == "\"") { campo = campo "\""; i++ }
                else q = 0
            } else campo = campo c
        } else if (c == "\"") q = 1
        else if (c == ",") { gsub(/\t/, " ", campo); saida = saida campo "\t"; campo = "" }
        else campo = campo c
    }
    gsub(/\t/, " ", campo)
    print saida campo
}
