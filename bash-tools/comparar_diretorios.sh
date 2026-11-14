#!/usr/bin/env bash
# Compara dois diretórios (nomes de arquivo e conteúdo).
# Uso: comparar_diretorios.sh <dir1> <dir2>
# Saída: 0 idênticos, 3 diferentes, 1 uso, 2 diretório inexistente.
set -euo pipefail

uso() {
  cat <<'USO'
Uso: comparar_diretorios.sh <dir1> <dir2>
Mostra: "so em <dir>: arq" e "diferente: arq" (conteúdo distinto).
USO
}

case "${1:-}" in
  -h|--help) uso; exit 0 ;;
esac
if (( $# != 2 )); then
  echo "erro: informe dois diretórios" >&2; uso >&2; exit 1
fi
d1="${1%/}"; d2="${2%/}"
for d in "$d1" "$d2"; do
  [[ -d "$d" ]] || { echo "erro: diretório inexistente: $d" >&2; exit 2; }
done

lista() { (cd "$1" && find . -type f | sed 's|^\./||' | LC_ALL=C sort); }
l1="$(lista "$d1")"; l2="$(lista "$d2")"

dif=0
while IFS= read -r rel; do
  [[ -z "$rel" ]] && continue
  if [[ ! -f "$d2/$rel" ]]; then
    echo "so em $d1: $rel"; dif=1
  elif ! cmp -s "$d1/$rel" "$d2/$rel"; then
    echo "diferente: $rel"; dif=1
  fi
done <<< "$l1"
while IFS= read -r rel; do
  [[ -z "$rel" ]] && continue
  if [[ ! -f "$d1/$rel" ]]; then
    echo "so em $d2: $rel"; dif=1
  fi
done <<< "$l2"

if (( dif )); then exit 3; fi
echo "diretorios identicos"
