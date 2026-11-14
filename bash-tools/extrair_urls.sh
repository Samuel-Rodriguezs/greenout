#!/usr/bin/env bash
# Extrai URLs http/https de um texto (arquivo ou entrada padrão).
# Uso: extrair_urls.sh [-u] [arquivo]
# Saída: 0 ok, 1 uso, 2 arquivo inexistente.
set -euo pipefail

uso() {
  cat <<'USO'
Uso: extrair_urls.sh [-u] [arquivo]
Lê o arquivo (ou stdin) e imprime as URLs http(s) encontradas.
  -u   remove repetidas (ordem de aparição preservada)
USO
}

unicas=0
arq=""
for arg in "$@"; do
  case "$arg" in
    -h|--help) uso; exit 0 ;;
    -u) unicas=1 ;;
    -*) echo "erro: opção desconhecida: $arg" >&2; exit 1 ;;
    *) arq="$arg" ;;
  esac
done

if [[ -n "$arq" && ! -f "$arq" ]]; then
  echo "erro: arquivo inexistente: $arq" >&2; exit 2
fi

extrair() {
  { grep -oE "https?://[A-Za-z0-9._~:/?#@!\$&*+=%-]+" "${arq:-/dev/stdin}" || true; } \
    | sed -E 's/[.,;:!?)]+$//'
}

if (( unicas )); then
  extrair | awk '!vistos[$0]++'
else
  extrair
fi
