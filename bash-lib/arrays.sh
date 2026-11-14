#!/usr/bin/env bash
# arrays.sh - biblioteca de operacoes sobre listas e arrays associativos.
# Funcoes: arr_sum, arr_max, arr_min, arr_sort, arr_unique, arr_reverse,
#          arr_contains, arr_freq
# Codigos de saida: 0 ok | 1 erro/nao encontrado/vazio | 2 uso incorreto
set -euo pipefail

arr_uso() {
  cat <<'USO'
Uso: arrays.sh <funcao> ITEM...
  sum N...        soma inteiros
  max N...        maior inteiro
  min N...        menor inteiro
  sort N...       ordena numericamente (um por linha)
  unique ITEM...  remove repetidos mantendo a ordem
  reverse ITEM... inverte a ordem
  contains V ITEM...  sai 0 se V estiver na lista, 1 caso contrario
  freq PALAVRA... frequencia (array associativo): "palavra contagem"
Saida: 0 ok, 1 erro/vazio, 2 uso incorreto.
USO
}

arr_inteiros() {
  local x
  for x in "$@"; do [[ $x =~ ^-?[0-9]+$ ]] || return 1; done
}

arr_sum() {
  arr_inteiros "$@" || return 1
  local t=0 x
  for x in "$@"; do t=$(( t + x )); done
  printf '%d\n' "$t"
}

arr_max() {
  (( $# > 0 )) && arr_inteiros "$@" || return 1
  local m="$1" x
  for x in "$@"; do if (( x > m )); then m=$x; fi; done
  printf '%d\n' "$m"
}

arr_min() {
  (( $# > 0 )) && arr_inteiros "$@" || return 1
  local m="$1" x
  for x in "$@"; do if (( x < m )); then m=$x; fi; done
  printf '%d\n' "$m"
}

arr_sort() {
  arr_inteiros "$@" || return 1
  if (( $# == 0 )); then return 0; fi
  printf '%s\n' "$@" | sort -n
}

arr_unique() {
  local -A visto=()
  local x
  for x in "$@"; do
    if [[ -z ${visto[$x]+x} ]]; then visto[$x]=1; printf '%s\n' "$x"; fi
  done
}

arr_reverse() {
  local i
  for ((i = $#; i >= 1; i--)); do printf '%s\n' "${!i}"; done
}

arr_contains() {
  (( $# >= 1 )) || return 2
  local alvo="$1" x
  shift
  for x in "$@"; do if [[ $x == "$alvo" ]]; then return 0; fi; done
  return 1
}

# Conta ocorrencias com array associativo; ordena por contagem desc, depois nome.
arr_freq() {
  (( $# > 0 )) || return 1
  local -A c=()
  local w k
  for w in "$@"; do c[$w]=$(( ${c[$w]:-0} + 1 )); done
  for k in "${!c[@]}"; do printf '%s %d\n' "$k" "${c[$k]}"; done | LC_ALL=C sort -k2,2nr -k1,1
}

arr_main() {
  case "${1-}" in
    -h | --help) arr_uso; return 0 ;;
    "") arr_uso >&2; return 2 ;;
  esac
  local f="arr_$1"
  shift
  case "$f" in
    arr_sum | arr_max | arr_min | arr_sort | arr_unique | arr_reverse | arr_contains | arr_freq) ;;
    *) echo "arrays.sh: funcao desconhecida" >&2; return 2 ;;
  esac
  local rc=0
  "$f" "$@" || rc=$?
  if (( rc != 0 )) && [[ $f != arr_contains ]]; then
    echo "arrays.sh: falha em ${f#arr_} (entrada invalida ou vazia)" >&2
  fi
  return "$rc"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then arr_main "$@"; fi
