#!/usr/bin/env bash
# Gera um índice em Markdown com os arquivos de uma pasta (recursivo).
# Uso: indice_markdown.sh <pasta> [saida.md]
# Saída: 0 ok, 1 uso, 2 pasta inexistente.
set -euo pipefail

uso() {
  cat <<'USO'
Uso: indice_markdown.sh <pasta> [saida.md]
Imprime uma lista Markdown de links para os arquivos. Com saida.md, grava nele.
USO
}

case "${1:-}" in
  -h|--help) uso; exit 0 ;;
  "") echo "erro: informe a pasta" >&2; uso >&2; exit 1 ;;
esac
pasta="${1%/}"
saida="${2:-}"
if [[ ! -d "$pasta" ]]; then
  echo "erro: pasta inexistente: $pasta" >&2; exit 2
fi

gerar() {
  echo "# Índice de $(basename "$pasta")"
  echo
  (cd "$pasta" && find . -type f | sed 's|^\./||' | LC_ALL=C sort) | while IFS= read -r rel; do
    # ignora o próprio arquivo de saída
    if [[ -n "$saida" && "$(basename "$saida")" == "$rel" ]]; then continue; fi
    echo "- [$rel]($rel)"
  done
}

if [[ -n "$saida" ]]; then
  tmp="$(mktemp)"
  trap 'rm -f "$tmp"' EXIT
  gerar > "$tmp"
  cat "$tmp" > "$saida"
  echo "gerado: $saida"
else
  gerar
fi
