#!/usr/bin/env bash
# forca.sh - jogo da forca. A palavra vem por parametro; as tentativas por stdin
# (uma por linha: uma letra, ou a palavra inteira para arriscar).
# Saida: 0 venceu | 1 perdeu | 2 uso incorreto | 3 entrada acabou antes do fim
set -euo pipefail

uso() {
  cat <<'USO'
Uso: forca.sh [-v VIDAS] PALAVRA < tentativas
  PALAVRA   somente letras a-z (sem acentos)
  -v VIDAS  numero de erros permitidos (padrao 6)
  -h        esta ajuda
Cada linha de stdin e uma letra ou um palpite da palavra inteira.
Saida: 0 venceu, 1 perdeu, 2 uso incorreto, 3 entrada acabou antes do fim.
USO
}

vidas=6
if [[ ${1-} == --help ]]; then uso; exit 0; fi
while getopts ":v:h" opt; do
  case "$opt" in
    v) vidas=$OPTARG ;;
    h) uso; exit 0 ;;
    :) echo "forca.sh: -$OPTARG exige valor" >&2; exit 2 ;;
    *) echo "forca.sh: opcao invalida -$OPTARG" >&2; exit 2 ;;
  esac
done
shift $((OPTIND - 1))
if [[ ${1-} == --help ]]; then uso; exit 0; fi
if (( $# != 1 )); then uso >&2; exit 2; fi
palavra=${1,,}
if [[ ! $palavra =~ ^[a-z]+$ ]]; then echo "forca.sh: a palavra deve ter apenas letras a-z" >&2; exit 2; fi
if [[ ! $vidas =~ ^[1-9][0-9]*$ ]]; then echo "forca.sh: VIDAS deve ser inteiro positivo" >&2; exit 2; fi

tentadas=""
erros=0

# Monta a mascara, ex.: "_ a _ _"
mascara() {
  local out="" i c
  for ((i = 0; i < ${#palavra}; i++)); do
    c=${palavra:i:1}
    if [[ $tentadas == *"$c"* ]]; then out+="$c "; else out+="_ "; fi
  done
  printf '%s' "${out% }"
}

completa() {
  local i
  for ((i = 0; i < ${#palavra}; i++)); do
    [[ $tentadas == *"${palavra:i:1}"* ]] || return 1
  done
}

echo "Palavra: $(mascara) | vidas: $((vidas - erros))"
while IFS= read -r linha || [[ -n $linha ]]; do
  linha=${linha,,}
  linha=${linha//[[:space:]]/}
  if [[ -z $linha ]]; then continue; fi
  if [[ ! $linha =~ ^[a-z]+$ ]]; then echo "Entrada invalida: use letras a-z"; continue; fi
  if (( ${#linha} > 1 )); then
    if [[ $linha == "$palavra" ]]; then
      echo "Venceu! A palavra era $palavra"
      exit 0
    fi
    erros=$((erros + 1))
    echo "Palpite errado."
  elif [[ $tentadas == *"$linha"* ]]; then
    echo "Letra '$linha' ja tentada."
    continue
  else
    tentadas+=$linha
    if [[ $palavra == *"$linha"* ]]; then echo "Acertou '$linha'."; else erros=$((erros + 1)); echo "Errou '$linha'."; fi
  fi
  echo "Palavra: $(mascara) | vidas: $((vidas - erros))"
  if completa; then echo "Venceu! A palavra era $palavra"; exit 0; fi
  if (( erros >= vidas )); then echo "Perdeu! A palavra era $palavra"; exit 1; fi
done
echo "Entrada encerrada antes do fim do jogo."
exit 3
