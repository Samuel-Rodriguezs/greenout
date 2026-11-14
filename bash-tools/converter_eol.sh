#!/usr/bin/env bash
# Converte finais de linha entre CRLF (dos) e LF (unix), no próprio arquivo.
# Uso: converter_eol.sh <para-lf|para-crlf> <arquivo> [...]
# Saída: 0 ok, 1 uso, 2 arquivo inexistente.
set -euo pipefail

uso() {
  cat <<'USO'
Uso: converter_eol.sh <para-lf|para-crlf> <arquivo> [arquivo ...]
Converte os arquivos no lugar.
USO
}

case "${1:-}" in
  -h|--help) uso; exit 0 ;;
  "") echo "erro: informe o modo" >&2; uso >&2; exit 1 ;;
esac
modo="$1"; shift
if [[ "$modo" != "para-lf" && "$modo" != "para-crlf" ]]; then
  echo "erro: modo inválido: $modo" >&2; exit 1
fi
if (( $# == 0 )); then
  echo "erro: informe ao menos um arquivo" >&2; exit 1
fi

for arq in "$@"; do
  if [[ ! -f "$arq" ]]; then
    echo "erro: arquivo inexistente: $arq" >&2; exit 2
  fi
  if [[ "$modo" == "para-lf" ]]; then
    sed -i 's/\r$//' "$arq"
  else
    # primeiro normaliza para LF, depois adiciona CR
    sed -i -e 's/\r$//' -e 's/$/\r/' "$arq"
  fi
  echo "convertido: $arq ($modo)"
done
