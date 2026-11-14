#!/usr/bin/env bash
# Valida arquivos JSON usando python3 (módulo json).
# Uso: validar_json.sh <arquivo.json> [...]
# Saída: 0 todos válidos, 1 uso, 2 arquivo inexistente, 3 JSON inválido.
set -euo pipefail

uso() {
  cat <<'USO'
Uso: validar_json.sh <arquivo.json> [outro.json ...]
Imprime "ok: arquivo" ou "invalido: arquivo (motivo)" para cada arquivo.
USO
}

case "${1:-}" in
  -h|--help) uso; exit 0 ;;
  "") echo "erro: informe ao menos um arquivo" >&2; uso >&2; exit 1 ;;
esac

status=0
for arq in "$@"; do
  if [[ ! -f "$arq" ]]; then
    echo "erro: arquivo inexistente: $arq" >&2
    exit 2
  fi
  if msg="$(python3 -c 'import json,sys; json.load(open(sys.argv[1], encoding="utf-8"))' "$arq" 2>&1)"; then
    echo "ok: $arq"
  else
    echo "invalido: $arq ($(printf '%s' "$msg" | tail -n1))"
    status=3
  fi
done
exit "$status"
