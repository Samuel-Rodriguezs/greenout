#!/usr/bin/env bash
# menu.sh - menu de linha de comando lido via stdin.
# Cada item e "ROTULO:COMANDO" (separado no primeiro ':'). A opcao 0 sai.
# Saida: 0 saiu pela opcao 0 | 2 uso incorreto | 3 stdin acabou sem escolher 0
set -euo pipefail

uso() {
  cat <<'USO'
Uso: menu.sh [-t TITULO] "ROTULO:COMANDO" ... < escolhas
  Mostra um menu numerado; le o numero da opcao em stdin (uma por linha),
  executa o comando com bash -c e volta ao menu. 0 encerra.
  -t TITULO  titulo do menu (padrao: Menu)
  -h         esta ajuda
Saida: 0 saiu pela opcao 0, 2 uso incorreto, 3 entrada encerrada.
USO
}

titulo="Menu"
if [[ ${1-} == --help ]]; then uso; exit 0; fi
while getopts ":t:h" opt; do
  case "$opt" in
    t) titulo=$OPTARG ;;
    h) uso; exit 0 ;;
    :) echo "menu.sh: -$OPTARG exige valor" >&2; exit 2 ;;
    *) echo "menu.sh: opcao invalida -$OPTARG" >&2; exit 2 ;;
  esac
done
shift $((OPTIND - 1))
if [[ ${1-} == --help ]]; then uso; exit 0; fi
if (( $# == 0 )); then uso >&2; exit 2; fi

rotulos=()
comandos=()
for item in "$@"; do
  if [[ $item != *:* || -z ${item%%:*} || -z ${item#*:} ]]; then
    echo "menu.sh: item invalido '$item' (use ROTULO:COMANDO)" >&2
    exit 2
  fi
  rotulos+=("${item%%:*}")
  comandos+=("${item#*:}")
done

mostrar() {
  echo "== $titulo =="
  local i
  for i in "${!rotulos[@]}"; do printf '%d) %s\n' $((i + 1)) "${rotulos[i]}"; done
  echo "0) Sair"
}

mostrar
while IFS= read -r escolha || [[ -n $escolha ]]; do
  escolha=${escolha//[[:space:]]/}
  if [[ $escolha == 0 ]]; then echo "Ate logo!"; exit 0; fi
  if [[ $escolha =~ ^[0-9]+$ ]] && (( 10#$escolha >= 1 && 10#$escolha <= ${#comandos[@]} )); then
    idx=$((10#$escolha - 1))
    rc=0
    bash -c "${comandos[idx]}" || rc=$?
    if (( rc != 0 )); then echo "Comando '${rotulos[idx]}' terminou com codigo $rc"; fi
  else
    echo "Opcao invalida: '$escolha'"
  fi
  mostrar
done
echo "Entrada encerrada."
exit 3
