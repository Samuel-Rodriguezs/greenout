#!/usr/bin/env bash
# csv2tsv.sh - converte CSV em TSV usando awk.
# Trata campos entre aspas (virgulas internas e "" escapado); tabs dentro de
# campos viram espaco. Nao suporta quebra de linha dentro de campo.
# Saida: 0 ok | 1 aspas nao fechadas | 2 uso incorreto / arquivo inexistente
set -euo pipefail

uso() {
  cat <<'USO'
Uso: csv2tsv.sh [-d DELIM] [ARQUIVO]
  Le ARQUIVO (ou stdin) e escreve TSV na saida padrao.
  -d DELIM  separador de entrada com 1 caractere (padrao: ,)
  -h        esta ajuda
Saida: 0 ok, 1 aspas nao fechadas, 2 uso incorreto.
USO
}

delim=","
if [[ ${1-} == --help ]]; then uso; exit 0; fi
while getopts ":d:h" opt; do
  case "$opt" in
    d) delim=$OPTARG ;;
    h) uso; exit 0 ;;
    :) echo "csv2tsv.sh: -$OPTARG exige valor" >&2; exit 2 ;;
    *) echo "csv2tsv.sh: opcao invalida -$OPTARG" >&2; exit 2 ;;
  esac
done
shift $((OPTIND - 1))
if [[ ${1-} == --help ]]; then uso; exit 0; fi
if [[ ${#delim} -ne 1 ]]; then echo "csv2tsv.sh: DELIM deve ter 1 caractere" >&2; exit 2; fi
if (( $# > 1 )); then uso >&2; exit 2; fi
entrada=${1:--}
if [[ $entrada != - && ! -f $entrada ]]; then
  echo "csv2tsv.sh: arquivo nao encontrado: $entrada" >&2
  exit 2
fi

awk -v d="$delim" '
function emitir() {
  gsub(/\t/, " ", campo)
  saida = saida (primeiro ? "" : "\t") campo
  campo = ""; primeiro = 0
}
{
  linha = $0
  sub(/\r$/, "", linha)
  n = length(linha); saida = ""; campo = ""; dentro = 0; primeiro = 1
  for (i = 1; i <= n; i++) {
    c = substr(linha, i, 1)
    if (dentro) {
      if (c == "\"") {
        if (substr(linha, i + 1, 1) == "\"") { campo = campo "\""; i++ }
        else dentro = 0
      } else campo = campo c
    } else if (c == "\"") dentro = 1
    else if (c == d) emitir()
    else campo = campo c
  }
  if (dentro) { erro = NR; exit 1 }
  emitir()
  print saida
}
END { if (erro) { print "csv2tsv.sh: aspas nao fechadas na linha " erro > "/dev/stderr"; exit 1 } }
' "$entrada"
