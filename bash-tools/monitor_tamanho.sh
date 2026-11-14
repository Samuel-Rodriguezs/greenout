#!/usr/bin/env bash
# Verifica se o tamanho de uma pasta ultrapassa um limite (em KB).
# Uso: monitor_tamanho.sh <pasta> <limite_kb>
# Saída: 0 dentro do limite, 3 limite excedido, 1 uso, 2 pasta inexistente.
set -euo pipefail

uso() {
  cat <<'USO'
Uso: monitor_tamanho.sh <pasta> <limite_kb>
Soma o tamanho real (bytes) dos arquivos e compara com o limite em KB (1 KB = 1024 bytes).
USO
}

case "${1:-}" in
  -h|--help) uso; exit 0 ;;
esac
if (( $# != 2 )); then
  echo "erro: informe pasta e limite_kb" >&2; uso >&2; exit 1
fi
pasta="$1"; limite="$2"
if ! [[ "$limite" =~ ^[0-9]+$ ]]; then
  echo "erro: limite_kb deve ser inteiro não negativo" >&2; exit 1
fi
if [[ ! -d "$pasta" ]]; then
  echo "erro: pasta inexistente: $pasta" >&2; exit 2
fi

bytes=0
while IFS= read -r -d '' arq; do
  t="$(stat -c %s "$arq")"
  bytes=$((bytes + t))
done < <(find "$pasta" -type f -print0)
kb=$(( (bytes + 1023) / 1024 ))

if (( kb > limite )); then
  echo "ALERTA: $pasta usa ${kb} KB (limite ${limite} KB)"
  exit 3
fi
echo "ok: $pasta usa ${kb} KB (limite ${limite} KB)"
