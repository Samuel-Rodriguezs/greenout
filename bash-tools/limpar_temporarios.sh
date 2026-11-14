#!/usr/bin/env bash
# Remove arquivos temporários (*.tmp, *.bak, *~) mais antigos que N dias.
# Uso: limpar_temporarios.sh [--dry-run] <pasta> <dias>
# Saída: 0 ok, 1 uso, 2 pasta inexistente.
set -euo pipefail

uso() {
  cat <<'USO'
Uso: limpar_temporarios.sh [--dry-run] <pasta> <dias>
Apaga *.tmp, *.bak e *~ com modificação anterior a <dias> dias.
  --dry-run   só lista
USO
}

dry=0
args=()
for arg in "$@"; do
  case "$arg" in
    -h|--help) uso; exit 0 ;;
    --dry-run) dry=1 ;;
    *) args+=("$arg") ;;
  esac
done
if (( ${#args[@]} != 2 )); then
  echo "erro: informe pasta e dias" >&2; uso >&2; exit 1
fi
pasta="${args[0]}"; dias="${args[1]}"
if ! [[ "$dias" =~ ^[0-9]+$ ]]; then
  echo "erro: dias deve ser inteiro não negativo" >&2; exit 1
fi
if [[ ! -d "$pasta" ]]; then
  echo "erro: pasta inexistente: $pasta" >&2; exit 2
fi

n=0
while IFS= read -r -d '' arq; do
  if (( dry )); then
    echo "[dry-run] $arq"
  else
    rm -f -- "$arq"
    echo "removido: $arq"
  fi
  n=$((n + 1))
done < <(find "$pasta" -type f \( -name '*.tmp' -o -name '*.bak' -o -name '*~' \) -mtime +"$dias" -print0)
echo "total: $n"
