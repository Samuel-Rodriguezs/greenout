#!/usr/bin/env bash
# Organiza arquivos de uma pasta em subpastas nomeadas pela extensão.
# Uso: organizar_downloads.sh [--dry-run] <pasta>
# Saída: 0 ok, 1 erro de uso, 2 pasta inexistente.
set -euo pipefail

uso() {
  cat <<'USO'
Uso: organizar_downloads.sh [--dry-run] <pasta>
Move os arquivos da pasta para subpastas por extensão (ex.: pdf/, txt/).
Arquivos sem extensão vão para sem_extensao/.
  --dry-run   apenas mostra o que seria movido
  -h, --help  mostra esta ajuda
USO
}

dry=0
pasta=""
for arg in "$@"; do
  case "$arg" in
    -h|--help) uso; exit 0 ;;
    --dry-run) dry=1 ;;
    -*) echo "erro: opção desconhecida: $arg" >&2; exit 1 ;;
    *) pasta="$arg" ;;
  esac
done

if [[ -z "$pasta" ]]; then
  echo "erro: informe a pasta" >&2; uso >&2; exit 1
fi
if [[ ! -d "$pasta" ]]; then
  echo "erro: pasta inexistente: $pasta" >&2; exit 2
fi

total=0
while IFS= read -r -d '' arq; do
  nome="$(basename "$arq")"
  if [[ "$nome" == *.* && "$nome" != .* ]]; then
    ext="${nome##*.}"
    ext="$(printf '%s' "$ext" | tr '[:upper:]' '[:lower:]')"
  else
    ext="sem_extensao"
  fi
  destino="$pasta/$ext"
  if (( dry )); then
    echo "[dry-run] $nome -> $ext/"
  else
    mkdir -p "$destino"
    mv -n -- "$arq" "$destino/"
    echo "$nome -> $ext/"
  fi
  total=$((total + 1))
done < <(find "$pasta" -maxdepth 1 -type f -print0 | sort -z)

echo "total: $total"
