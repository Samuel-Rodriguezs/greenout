#!/usr/bin/env bash
# rpn.sh - calculadora em notacao polonesa reversa (inteiros).
# Operadores: + - * / % ^ . Ex.: rpn.sh 3 4 + 2 '*'   ou   rpn.sh "3 4 + 2 *"
# Saida: 0 ok | 1 erro de calculo (pilha, divisao por zero, token invalido) | 2 uso incorreto
set -euo pipefail

uso() {
  cat <<'USO'
Uso: rpn.sh EXPRESSAO...
  Avalia uma expressao RPN de inteiros; tokens separados por espaco
  (em um unico argumento ou em varios). Operadores: + - * / % ^
  Exemplo: rpn.sh "5 1 2 + 4 * + 3 -"   -> 14
Saida: 0 ok, 1 erro de calculo, 2 uso incorreto.
USO
}

# rpn_avaliar TOKEN... : imprime o resultado ou mensagem em stderr (retorno 1).
rpn_avaliar() {
  local -a pilha=()
  local t a b r
  for t in "$@"; do
    if [[ $t =~ ^-?[0-9]+$ ]]; then
      if [[ $t == -* ]]; then pilha+=("-$((10#${t#-}))"); else pilha+=("$((10#$t))"); fi
      continue
    fi
    case "$t" in
      + | - | \* | / | % | ^) ;;
      *) echo "rpn: token invalido '$t'" >&2; return 1 ;;
    esac
    if (( ${#pilha[@]} < 2 )); then echo "rpn: pilha insuficiente para '$t'" >&2; return 1; fi
    b=${pilha[-1]}
    a=${pilha[-2]}
    unset 'pilha[-1]' 'pilha[-1]'
    case "$t" in
      + ) r=$(( a + b )) ;;
      - ) r=$(( a - b )) ;;
      \*) r=$(( a * b )) ;;
      / | %)
        if (( b == 0 )); then echo "rpn: divisao por zero" >&2; return 1; fi
        if [[ $t == / ]]; then r=$(( a / b )); else r=$(( a % b )); fi
        ;;
      ^ )
        if (( b < 0 )); then echo "rpn: expoente negativo" >&2; return 1; fi
        r=$(( a ** b ))
        ;;
    esac
    pilha+=("$r")
  done
  if (( ${#pilha[@]} == 0 )); then echo "rpn: expressao vazia" >&2; return 1; fi
  if (( ${#pilha[@]} > 1 )); then echo "rpn: sobraram ${#pilha[@]} valores na pilha" >&2; return 1; fi
  printf '%s\n' "${pilha[0]}"
}

main() {
  case "${1-}" in
    -h | --help) uso; return 0 ;;
    "") uso >&2; return 2 ;;
  esac
  local -a tokens
  read -ra tokens <<<"$*"
  rpn_avaliar "${tokens[@]}"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then main "$@"; fi
