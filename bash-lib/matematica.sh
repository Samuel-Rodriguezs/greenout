#!/usr/bin/env bash
# matematica.sh - funcoes de matematica inteira: gcd, mmc, primos, fatorial, bases.
# Codigos de saida: 0 ok | 1 resultado negativo (ex.: nao e primo) | 2 entrada invalida/uso incorreto
set -euo pipefail

mat_uso() {
  cat <<'USO'
Uso: matematica.sh <funcao> args...
  gcd A B             maximo divisor comum
  lcm A B             minimo multiplo comum
  primo N             imprime sim/nao; sai 0 se primo, 1 se nao
  primos_ate N        lista os primos <= N
  fatorial N          N! (0 <= N <= 20)
  converter N DE PARA converte N da base DE para a base PARA (2..36)
Saida: 0 ok, 1 nao e primo, 2 entrada invalida/uso incorreto.
USO
}

mat_nat() { [[ ${1-} =~ ^[0-9]+$ ]]; }

mat_gcd() {
  (( $# == 2 )) && mat_nat "$1" && mat_nat "$2" || return 2
  local a=$1 b=$2 t
  while (( b != 0 )); do t=$(( a % b )); a=$b; b=$t; done
  printf '%d\n' "$a"
}

mat_lcm() {
  (( $# == 2 )) && mat_nat "$1" && mat_nat "$2" || return 2
  if (( $1 == 0 || $2 == 0 )); then echo 0; return 0; fi
  local g
  g=$(mat_gcd "$1" "$2")
  printf '%d\n' $(( $1 / g * $2 ))
}

# Retorna 0 se primo (sem imprimir); usado internamente.
mat_eh_primo() {
  local n=$1 i
  (( n >= 2 )) || return 1
  for ((i = 2; i * i <= n; i++)); do
    if (( n % i == 0 )); then return 1; fi
  done
  return 0
}

mat_primo() {
  (( $# == 1 )) && mat_nat "$1" || return 2
  if mat_eh_primo "$1"; then echo sim; else echo nao; return 1; fi
}

mat_primos_ate() {
  (( $# == 1 )) && mat_nat "$1" || return 2
  local i
  for ((i = 2; i <= $1; i++)); do
    if mat_eh_primo "$i"; then printf '%d\n' "$i"; fi
  done
}

mat_fatorial() {
  (( $# == 1 )) && mat_nat "$1" || return 2
  (( 10#$1 <= 20 )) || { echo "matematica.sh: N > 20 estoura 64 bits" >&2; return 2; }
  local r=1 i
  for ((i = 2; i <= 10#$1; i++)); do r=$(( r * i )); done
  printf '%d\n' "$r"
}

mat_converter() {
  (( $# == 3 )) && mat_nat "$2" && mat_nat "$3" || return 2
  local num="${1^^}" de=$(( 10#$2 )) para=$(( 10#$3 ))
  (( de >= 2 && de <= 36 && para >= 2 && para <= 36 )) || return 2
  local digitos=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ
  [[ $num =~ ^[0-9A-Z]+$ ]] || return 2
  local valor=0 i c pos
  for ((i = 0; i < ${#num}; i++)); do
    c=${num:i:1}
    pos=${digitos%%"$c"*}
    pos=${#pos}
    (( pos < de )) || { echo "matematica.sh: digito '$c' invalido na base $de" >&2; return 2; }
    valor=$(( valor * de + pos ))
  done
  if (( valor == 0 )); then echo 0; return 0; fi
  local saida=""
  while (( valor > 0 )); do saida="${digitos:valor % para:1}$saida"; valor=$(( valor / para )); done
  printf '%s\n' "$saida"
}

mat_main() {
  case "${1-}" in
    -h | --help) mat_uso; return 0 ;;
    "") mat_uso >&2; return 2 ;;
  esac
  local f="mat_$1"
  shift
  case "$f" in
    mat_gcd | mat_lcm | mat_primo | mat_primos_ate | mat_fatorial | mat_converter) ;;
    *) echo "matematica.sh: funcao desconhecida" >&2; return 2 ;;
  esac
  local rc=0
  "$f" "$@" || rc=$?
  if (( rc == 2 )); then echo "matematica.sh: argumentos invalidos" >&2; fi
  return "$rc"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then mat_main "$@"; fi
