#!/usr/bin/env bash
# pascal.sh - imprime o triangulo de Pascal com N linhas (1 <= N <= 30).
# Opcao -c centraliza o triangulo. Saida: 0 ok | 2 argumento invalido
set -euo pipefail

uso() {
  cat <<'USO'
Uso: pascal.sh [-c] N
  Imprime as N primeiras linhas do triangulo de Pascal (1 <= N <= 30).
  -c   centraliza as linhas
  -h   esta ajuda
Saida: 0 ok, 2 argumento invalido.
USO
}

centralizar=0
if [[ ${1-} == --help ]]; then uso; exit 0; fi
while getopts ":ch" opt; do
  case "$opt" in
    c) centralizar=1 ;;
    h) uso; exit 0 ;;
    *) echo "pascal.sh: opcao invalida -$OPTARG" >&2; exit 2 ;;
  esac
done
shift $((OPTIND - 1))
if [[ ${1-} == --help ]]; then uso; exit 0; fi
if (( $# != 1 )) || [[ ! $1 =~ ^[0-9]+$ ]] || (( 10#$1 < 1 || 10#$1 > 30 )); then
  echo "pascal.sh: informe N entre 1 e 30" >&2
  exit 2
fi
n=$((10#$1))

linhas=()
for ((i = 0; i < n; i++)); do
  c=1
  partes=()
  for ((k = 0; k <= i; k++)); do
    partes+=("$c")
    c=$(( c * (i - k) / (k + 1) ))
  done
  linhas+=("${partes[*]}")
done

maior=${#linhas[$((n - 1))]}
for l in "${linhas[@]}"; do
  if (( centralizar )); then
    printf '%*s%s\n' $(( (maior - ${#l}) / 2 )) '' "$l"
  else
    printf '%s\n' "$l"
  fi
done
