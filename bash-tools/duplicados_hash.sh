#!/usr/bin/env bash
# Procura arquivos duplicados (mesmo conteúdo) usando sha256sum.
# Uso: duplicados_hash.sh <pasta>
# Saída: 0 sem duplicados, 3 duplicados encontrados, 1 uso, 2 pasta inexistente.
set -euo pipefail

uso() {
  cat <<'USO'
Uso: duplicados_hash.sh <pasta>
Lista grupos de arquivos com o mesmo sha256 (busca recursiva).
Código de saída: 0 = nenhum duplicado, 3 = há duplicados.
USO
}

case "${1:-}" in
  -h|--help) uso; exit 0 ;;
  "") echo "erro: informe a pasta" >&2; uso >&2; exit 1 ;;
esac
pasta="$1"
if [[ ! -d "$pasta" ]]; then
  echo "erro: pasta inexistente: $pasta" >&2; exit 2
fi

tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT
find "$pasta" -type f -print0 | sort -z | xargs -0 -r sha256sum > "$tmp"

# hashes que aparecem mais de uma vez
dups="$(cut -d' ' -f1 "$tmp" | sort | uniq -d)"
if [[ -z "$dups" ]]; then
  echo "nenhum duplicado"
  exit 0
fi

while IFS= read -r h; do
  echo "hash $h"
  grep "^$h " "$tmp" | sed 's/^[0-9a-f]*  /  /'
done <<< "$dups"
exit 3
