#!/bin/sh
# subst_lote.sh - substituicao em lote com regex estendida e backreferences.
# Uso: sh subst_lote.sh regras.tsv [arquivo]     (sem arquivo le a entrada padrao)
# Cada linha de regras.tsv: <regex><TAB><substituicao> (use \1..\9 na substituicao).
# Linhas vazias ou iniciadas por '#' sao ignoradas; linhas sem TAB geram aviso em
# stderr e sao puladas. As regras sao aplicadas em ordem.
[ -r "$1" ] || { echo "uso: $0 regras.tsv [arquivo]" >&2; exit 2; }
regras=$1; shift
tmp=$(mktemp) || exit 1
trap 'rm -f "$tmp"' EXIT
awk -F'\t' '
    /^[[:space:]]*(#|$)/ { next }
    NF < 2 { print "aviso: regra malformada na linha " NR > "/dev/stderr"; next }
    { gsub(/\001/, "", $1); gsub(/\001/, "", $2); print "s\001" $1 "\001" $2 "\001g" }
' "$regras" > "$tmp"
sed -E -f "$tmp" "$@"
