#!/usr/bin/env bash
# datas.sh - funcoes de data (GNU date -d): diferenca em dias, dia da semana, soma de dias.
# Datas no formato AAAA-MM-DD. Saida: 0 ok | 1 data invalida (ou ano nao bissexto) | 2 uso incorreto
set -euo pipefail

dat_uso() {
  cat <<'USO'
Uso: datas.sh <funcao> args...
  diff D1 D2        dias de D1 ate D2 (negativo se D2 < D1)
  dia_semana D      nome do dia da semana em portugues
  somar D N         data D + N dias (N pode ser negativo)
  bissexto ANO      sim/nao (sai 0 se bissexto, 1 se nao)
Saida: 0 ok, 1 data invalida, 2 uso incorreto.
USO
}

dat_valida() {
  [[ ${1-} =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]] || return 1
  local volta
  volta=$(TZ=UTC date -d "$1" +%F 2>/dev/null) || return 1
  [[ $volta == "$1" ]]
}

dat_diff() {
  (( $# == 2 )) || return 2
  dat_valida "$1" && dat_valida "$2" || return 1
  local e1 e2
  e1=$(TZ=UTC date -d "$1" +%s)
  e2=$(TZ=UTC date -d "$2" +%s)
  printf '%d\n' $(( (e2 - e1) / 86400 ))
}

dat_dia_semana() {
  (( $# == 1 )) || return 2
  dat_valida "$1" || return 1
  local nomes=(segunda-feira terca-feira quarta-feira quinta-feira sexta-feira sabado domingo)
  local n
  n=$(TZ=UTC date -d "$1" +%u)
  printf '%s\n' "${nomes[n - 1]}"
}

dat_somar() {
  (( $# == 2 )) && [[ $2 =~ ^[+-]?[0-9]+$ ]] || return 2
  dat_valida "$1" || return 1
  TZ=UTC date -d "$1 $2 days" +%F
}

dat_bissexto() {
  (( $# == 1 )) && [[ $1 =~ ^[0-9]+$ ]] || return 2
  local a=$(( 10#$1 ))
  if (( a % 400 == 0 || (a % 4 == 0 && a % 100 != 0) )); then echo sim; else echo nao; return 1; fi
}

dat_main() {
  case "${1-}" in
    -h | --help) dat_uso; return 0 ;;
    "") dat_uso >&2; return 2 ;;
  esac
  local f="dat_$1"
  shift
  case "$f" in
    dat_diff | dat_dia_semana | dat_somar | dat_bissexto) ;;
    *) echo "datas.sh: funcao desconhecida" >&2; return 2 ;;
  esac
  local rc=0
  "$f" "$@" || rc=$?
  if (( rc == 1 )) && [[ $f != dat_bissexto ]]; then echo "datas.sh: data invalida (use AAAA-MM-DD)" >&2
  elif (( rc == 2 )); then echo "datas.sh: argumentos invalidos" >&2; fi
  return "$rc"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then dat_main "$@"; fi
