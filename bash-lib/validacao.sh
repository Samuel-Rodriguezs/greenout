#!/usr/bin/env bash
# validacao.sh - validadores: inteiro, e-mail, IPv4 e CPF (com digitos verificadores).
# Como CLI imprime "valido"/"invalido". Saida: 0 valido | 1 invalido | 2 uso incorreto
set -euo pipefail

val_uso() {
  cat <<'USO'
Uso: validacao.sh <tipo> VALOR
  inteiro VALOR   inteiro com sinal opcional
  email VALOR     endereco de e-mail simples
  ip VALOR        IPv4 (4 octetos 0-255, sem zeros a esquerda)
  cpf VALOR       CPF com ou sem pontuacao, com digitos verificadores
Saida: 0 valido, 1 invalido, 2 uso incorreto.
USO
}

val_inteiro() { [[ ${1-} =~ ^[+-]?[0-9]+$ ]]; }

val_email() {
  local re='^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$'
  [[ ${1-} =~ $re ]]
}

val_ip() {
  local re='^([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})$'
  [[ ${1-} =~ $re ]] || return 1
  local o
  for o in "${BASH_REMATCH[@]:1}"; do
    [[ $o =~ ^(0|[1-9][0-9]*)$ ]] || return 1
    (( o <= 255 )) || return 1
  done
}

val_cpf() {
  local c="${1-}"
  c=${c//./}
  c=${c//-/}
  [[ $c =~ ^[0-9]{11}$ ]] || return 1
  local rep
  printf -v rep '%*s' 11 ''
  rep=${rep// /${c:0:1}}
  [[ $c != "$rep" ]] || return 1
  local soma i dv
  for alvo in 9 10; do
    soma=0
    for ((i = 0; i < alvo; i++)); do soma=$(( soma + ${c:i:1} * (alvo + 1 - i) )); done
    dv=$(( (soma * 10) % 11 ))
    if (( dv == 10 )); then dv=0; fi
    [[ ${c:alvo:1} == "$dv" ]] || return 1
  done
}

val_main() {
  case "${1-}" in
    -h | --help) val_uso; return 0 ;;
  esac
  (( $# == 2 )) || { val_uso >&2; return 2; }
  local tipo="$1"
  case "$tipo" in
    inteiro | email | ip | cpf) ;;
    *) echo "validacao.sh: tipo desconhecido '$tipo'" >&2; return 2 ;;
  esac
  if "val_$tipo" "$2"; then echo valido; else echo invalido; return 1; fi
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then val_main "$@"; fi
