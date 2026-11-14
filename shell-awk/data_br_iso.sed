# data_br_iso.sed - converte datas dd/mm/aaaa em aaaa-mm-dd dentro do texto.
# Uso: sed -E -f data_br_iso.sed arquivo     (requer -E)
# Valida dia 01-31 e mes 01-12; datas fora disso ficam intactas.
s#\b(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/([0-9]{4})\b#\3-\2-\1#g
