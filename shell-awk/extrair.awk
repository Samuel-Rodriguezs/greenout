# extrair.awk - extrai e-mails ou enderecos IPv4 de um texto, um por linha.
# Uso: awk -v tipo=email -f extrair.awk texto.txt
#      awk -v tipo=ip    -f extrair.awk log.txt
# IPs so sao aceitos se todos os octetos estiverem entre 0 e 255.
BEGIN {
    if (tipo != "email" && tipo != "ip") {
        print "erro: use -v tipo=email|ip" > "/dev/stderr"; erro = 1; exit 1
    }
}
{
    resto = $0
    if (tipo == "email") re = "[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\\.[A-Za-z0-9-]+)*\\.[A-Za-z]{2,}"
    else re = "[0-9]{1,3}(\\.[0-9]{1,3}){3}"
    while (match(resto, re)) {
        achado = substr(resto, RSTART, RLENGTH)
        resto = substr(resto, RSTART + RLENGTH)
        if (tipo == "ip") {
            split(achado, o, ".")
            if (o[1] > 255 || o[2] > 255 || o[3] > 255 || o[4] > 255) continue
        }
        print achado
    }
}
END { if (erro) exit 1 }
