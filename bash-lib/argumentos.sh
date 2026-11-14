#!/usr/bin/env bash
# argumentos.sh - exemplo de parsing de argumentos com getopts e subcomandos.
# Opcoes globais (antes do subcomando): -v (verboso), -h (ajuda)
# Subcomandos:
#   saudar [-n NOME] [-g SAUDACAO] [-u]   (-n obrigatorio)
#   somar  [-m] N...                      (-m = media inteira)
#   inverter TEXTO
# Saida: 0 ok | 2 uso incorreto (opcao/subcomando/argumento invalido)
set -euo pipefail

arg_uso() {
  cat <<'USO'
Uso: argumentos.sh [-v] [-h] <subcomando> [opcoes] [args]
Subcomandos:
  saudar -n NOME [-g SAUDACAO] [-u]   imprime "<SAUDACAO>, NOME!" (-u: maiusculas)
  somar [-m] N...                     soma inteiros (-m: media inteira)
  inverter TEXTO                      inverte o texto
Saida: 0 ok, 2 uso incorreto.
USO
}

VERBOSO=0

arg_saudar() {
  local OPTIND=1 opt nome="" saud="Ola" maiusc=0
  while getopts ":n:g:u" opt; do
    case "$opt" in
      n) nome=$OPTARG ;;
      g) saud=$OPTARG ;;
      u) maiusc=1 ;;
      :) echo "saudar: a opcao -$OPTARG exige valor" >&2; return 2 ;;
      *) echo "saudar: opcao invalida -$OPTARG" >&2; return 2 ;;
    esac
  done
  [[ -n $nome ]] || { echo "saudar: -n NOME e obrigatorio" >&2; return 2; }
  local msg="$saud, $nome!"
  if (( maiusc )); then msg=${msg^^}; fi
  printf '%s\n' "$msg"
}

arg_somar() {
  local OPTIND=1 opt media=0
  while getopts ":m" opt; do
    case "$opt" in
      m) media=1 ;;
      *) echo "somar: opcao invalida -$OPTARG" >&2; return 2 ;;
    esac
  done
  shift $((OPTIND - 1))
  (( $# > 0 )) || { echo "somar: informe ao menos um numero" >&2; return 2; }
  local t=0 x
  for x in "$@"; do
    [[ $x =~ ^-?[0-9]+$ ]] || { echo "somar: '$x' nao e inteiro" >&2; return 2; }
    t=$(( t + x ))
  done
  if (( media )); then t=$(( t / $# )); fi
  printf '%d\n' "$t"
}

arg_inverter() {
  (( $# == 1 )) || { echo "inverter: informe exatamente um TEXTO" >&2; return 2; }
  local s="$1" out="" i
  for ((i = ${#s} - 1; i >= 0; i--)); do out+="${s:i:1}"; done
  printf '%s\n' "$out"
}

arg_main() {
  local OPTIND=1 opt
  if [[ ${1-} == --help ]]; then arg_uso; return 0; fi
  while getopts ":vh" opt; do
    case "$opt" in
      v) VERBOSO=1 ;;
      h) arg_uso; return 0 ;;
      *) echo "opcao global invalida -$OPTARG" >&2; return 2 ;;
    esac
  done
  shift $((OPTIND - 1))
  case "${1-}" in
    --help) arg_uso; return 0 ;;
    "") arg_uso >&2; return 2 ;;
  esac
  local sub="$1"
  shift
  if (( VERBOSO )); then echo "[verbose] subcomando: $sub" >&2; fi
  case "$sub" in
    saudar) arg_saudar "$@" ;;
    somar) arg_somar "$@" ;;
    inverter) arg_inverter "$@" ;;
    *) echo "subcomando desconhecido: $sub" >&2; return 2 ;;
  esac
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then arg_main "$@"; fi
