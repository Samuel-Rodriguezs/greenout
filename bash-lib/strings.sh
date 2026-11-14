#!/usr/bin/env bash
# strings.sh - biblioteca de funcoes de texto (use com `source` ou como CLI).
# Funcoes: str_trim, str_upper, str_lower, str_join, str_split, str_repeat,
#          str_pad_left, str_pad_right, str_len
# Codigos de saida: 0 ok | 1 argumento invalido | 2 uso incorreto
set -euo pipefail

str_uso() {
  cat <<'USO'
Uso: strings.sh <funcao> [argumentos...]
  trim TEXTO              remove espacos nas pontas
  upper TEXTO             converte para maiusculas
  lower TEXTO             converte para minusculas
  join SEP ITEM...        junta itens com o separador
  split SEP TEXTO         separa (SEP de 1 caractere), um item por linha
  repeat TEXTO N          repete TEXTO N vezes
  pad_left TEXTO LARG [C] completa a esquerda com C (padrao: espaco)
  pad_right TEXTO LARG [C] completa a direita
  len TEXTO               numero de caracteres
Saida: 0 ok, 1 argumento invalido, 2 uso incorreto.
USO
}

# Remove espacos em branco no inicio e no fim.
str_trim() {
  local s="${1-}"
  s="${s#"${s%%[![:space:]]*}"}"
  s="${s%"${s##*[![:space:]]}"}"
  printf '%s\n' "$s"
}

str_upper() { local s="${1-}"; printf '%s\n' "${s^^}"; }
str_lower() { local s="${1-}"; printf '%s\n' "${s,,}"; }
str_len() { local s="${1-}"; printf '%d\n' "${#s}"; }

# str_join SEP ITEM... : une os itens.
str_join() {
  (( $# >= 1 )) || return 1
  local sep="$1" out="" first=1 item
  shift
  for item in "$@"; do
    if (( first )); then out="$item"; first=0; else out+="$sep$item"; fi
  done
  printf '%s\n' "$out"
}

# str_split SEP TEXTO : imprime cada campo em uma linha.
str_split() {
  (( $# == 2 )) && [[ ${#1} -eq 1 ]] || return 1
  local -a partes=()
  IFS="$1" read -ra partes <<<"$2" || true
  local p
  for p in "${partes[@]+"${partes[@]}"}"; do printf '%s\n' "$p"; done
}

str_repeat() {
  (( $# == 2 )) && [[ $2 =~ ^[0-9]+$ ]] || return 1
  local out="" i
  for ((i = 0; i < $2; i++)); do out+="$1"; done
  printf '%s\n' "$out"
}

str_pad_left() {
  (( $# >= 2 )) && [[ $2 =~ ^[0-9]+$ ]] || return 1
  local s="$1" c="${3:- }" n
  n=$(( $2 - ${#s} ))
  if (( n > 0 )); then printf '%s%s\n' "$(str_repeat "$c" "$n")" "$s"; else printf '%s\n' "$s"; fi
}

str_pad_right() {
  (( $# >= 2 )) && [[ $2 =~ ^[0-9]+$ ]] || return 1
  local s="$1" c="${3:- }" n
  n=$(( $2 - ${#s} ))
  if (( n > 0 )); then printf '%s%s\n' "$s" "$(str_repeat "$c" "$n")"; else printf '%s\n' "$s"; fi
}

str_main() {
  case "${1-}" in
    -h | --help) str_uso; return 0 ;;
    "") str_uso >&2; return 2 ;;
  esac
  local f="str_$1"
  shift
  case "$f" in
    str_trim | str_upper | str_lower | str_len | str_join | str_split | str_repeat | str_pad_left | str_pad_right) ;;
    *) echo "strings.sh: funcao desconhecida" >&2; return 2 ;;
  esac
  local rc=0
  "$f" "$@" || rc=$?
  if (( rc != 0 )); then echo "strings.sh: argumentos invalidos para ${f#str_}" >&2; fi
  return "$rc"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then str_main "$@"; fi
