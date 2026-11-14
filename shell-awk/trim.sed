# trim.sed - remove espacos e tabs no inicio e no fim de cada linha.
# Uso: sed -E -f trim.sed arquivo     (requer -E)
s/^[[:space:]]+//
s/[[:space:]]+$//
