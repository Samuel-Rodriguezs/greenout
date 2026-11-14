# soma_tempo.awk - soma duracoes "hh:mm:ss" (uma por linha) e imprime o total.
# Uso: awk -f soma_tempo.awk duracoes.txt
# Horas podem ter 1 ou mais digitos; minutos e segundos devem ser 00-59.
# Linhas invalidas sao ignoradas e reportadas em stderr. Saida: hh:mm:ss.
/^[0-9]+:[0-5][0-9]:[0-5][0-9]$/ {
    split($0, t, ":")
    total += t[1] * 3600 + t[2] * 60 + t[3]
    next
}
NF { print "ignorada: " $0 > "/dev/stderr" }
END { printf "%02d:%02d:%02d\n", int(total / 3600), int(total % 3600 / 60), total % 60 }
