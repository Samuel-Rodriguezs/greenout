#!/usr/bin/env bash
# sequencias.sh - geradores de sequencias numericas: Fibonacci, Collatz,
# triangulares e numeros perfeitos.
# Saida: 0 ok | 2 argumento invalido / uso incorreto
set -euo pipefail

seq_uso() {
  cat <<'USO'
Uso: sequencias.sh <funcao> N
  fib N           primeiros N termos de Fibonacci (0 <= N <= 90), um por linha
  collatz N       sequencia de Collatz a partir de N (N >= 1)
  triangulares N  primeiros N numeros triangulares
  perfeitos N     numeros perfeitos <= N
Saida: 0 ok, 2 argumento invalido.
USO
}

seq_nat() { [[ ${1-} =~ ^[0-9]+$ ]]; }

seq_fib() {
  (( $# == 1 )) && seq_nat "$1" || return 2
  local n=$((10#$1)) a=0 b=1 t i
  (( n <= 90 )) || return 2
  for ((i = 0; i < n; i++)); do
    printf '%d\n' "$a"
    t=$(( a + b )); a=$b; b=$t
  done
}

seq_collatz() {
  (( $# == 1 )) && seq_nat "$1" || return 2
  local n=$((10#$1))
  (( n >= 1 )) || return 2
  printf '%d\n' "$n"
  while (( n != 1 )); do
    if (( n % 2 == 0 )); then n=$(( n / 2 )); else n=$(( 3 * n + 1 )); fi
    printf '%d\n' "$n"
  done
}

seq_triangulares() {
  (( $# == 1 )) && seq_nat "$1" || return 2
  local i
  for ((i = 1; i <= 10#$1; i++)); do printf '%d\n' $(( i * (i + 1) / 2 )); done
}

seq_perfeitos() {
  (( $# == 1 )) && seq_nat "$1" || return 2
  local n d soma
  for ((n = 2; n <= 10#$1; n++)); do
    soma=1
    for ((d = 2; d * d <= n; d++)); do
      if (( n % d == 0 )); then
        soma=$(( soma + d ))
        if (( d != n / d )); then soma=$(( soma + n / d )); fi
      fi
    done
    if (( soma == n )); then printf '%d\n' "$n"; fi
  done
}

seq_main() {
  case "${1-}" in
    -h | --help) seq_uso; return 0 ;;
    "") seq_uso >&2; return 2 ;;
  esac
  local f="seq_$1"
  shift
  case "$f" in
    seq_fib | seq_collatz | seq_triangulares | seq_perfeitos) ;;
    *) echo "sequencias.sh: funcao desconhecida" >&2; return 2 ;;
  esac
  local rc=0
  "$f" "$@" || rc=$?
  if (( rc != 0 )); then echo "sequencias.sh: argumento invalido" >&2; fi
  return "$rc"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then seq_main "$@"; fi
