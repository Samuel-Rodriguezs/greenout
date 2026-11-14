#!/usr/bin/env bash
# uso_disco.sh - relatorio de uso de disco por subdiretorio (somando bytes dos arquivos).
# Saida: 0 ok | 2 uso incorreto / diretorio inexistente
set -euo pipefail

uso() {
  cat <<'USO'
Uso: uso_disco.sh [-n TOP] [-b] DIRETORIO
  Lista os subdiretorios (e arquivos soltos) ordenados por tamanho, com percentual.
  -n TOP  mostra apenas os TOP maiores (padrao: todos)
  -b      tamanhos em bytes (padrao: formato legivel B/K/M/G)
  -h      esta ajuda
Saida: 0 ok, 2 uso incorreto.
USO
}

top=0
bytes=0
if [[ ${1-} == --help ]]; then uso; exit 0; fi
while getopts ":n:bh" opt; do
  case "$opt" in
    n) top=$OPTARG ;;
    b) bytes=1 ;;
    h) uso; exit 0 ;;
    :) echo "uso_disco.sh: -$OPTARG exige valor" >&2; exit 2 ;;
    *) echo "uso_disco.sh: opcao invalida -$OPTARG" >&2; exit 2 ;;
  esac
done
shift $((OPTIND - 1))
if [[ ${1-} == --help ]]; then uso; exit 0; fi
if (( $# != 1 )); then uso >&2; exit 2; fi
if [[ ! $top =~ ^[0-9]+$ ]]; then echo "uso_disco.sh: TOP deve ser inteiro" >&2; exit 2; fi
dir=$1
if [[ ! -d $dir ]]; then echo "uso_disco.sh: diretorio nao encontrado: $dir" >&2; exit 2; fi

# Soma bytes dos arquivos regulares abaixo de um caminho.
tamanho_dir() { find "$1" -type f -printf '%s\n' | awk '{ s += $1 } END { print s + 0 }'; }

# Formata bytes em B/K/M/G.
humano() {
  awk -v b="$1" 'BEGIN {
    split("B K M G T", u, " "); i = 1
    while (b >= 1024 && i < 5) { b /= 1024; i++ }
    if (i == 1) printf "%d%s", b, u[i]; else printf "%.1f%s", b, u[i]
  }'
}

registros=""
total=0
soltos=$(find "$dir" -maxdepth 1 -type f -printf '%s\n' | awk '{ s += $1 } END { print s + 0 }')
if (( soltos > 0 )); then
  registros+="$soltos"$'\t'"(arquivos soltos)"$'\n'
  total=$(( total + soltos ))
fi
while IFS= read -r -d '' sub; do
  t=$(tamanho_dir "$sub")
  registros+="$t"$'\t'"$(basename "$sub")/"$'\n'
  total=$(( total + t ))
done < <(find "$dir" -mindepth 1 -maxdepth 1 -type d -print0)

ordenado=""
if [[ -n $registros ]]; then
  ordenado=$(printf '%s' "$registros" | LC_ALL=C sort -t $'\t' -k1,1nr -k2,2)
  if (( top > 0 )); then ordenado=$(printf '%s\n' "$ordenado" | head -n "$top"); fi
fi

if [[ -n $ordenado ]]; then
  while IFS=$'\t' read -r t nome; do
    if (( bytes )); then tam=$t; else tam=$(humano "$t"); fi
    pct=$(awk -v t="$t" -v tot="$total" 'BEGIN { printf "%.1f", tot ? t * 100 / tot : 0 }')
    printf '%10s %6s%%  %s\n' "$tam" "$pct" "$nome"
  done <<<"$ordenado"
fi
if (( bytes )); then tam=$total; else tam=$(humano "$total"); fi
printf '%10s %6s%%  %s\n' "$tam" "100.0" "TOTAL"
