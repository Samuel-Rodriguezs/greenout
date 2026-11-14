#!/usr/bin/env bash
# Conta linhas de código por extensão em uma pasta (recursivo).
# Uso: contar_linhas_codigo.sh <pasta> [ext ...]
# Saída: 0 ok, 1 uso, 2 pasta inexistente.
set -euo pipefail

uso() {
  cat <<'USO'
Uso: contar_linhas_codigo.sh <pasta> [ext ...]
Soma as linhas dos arquivos por extensão. Sem extensões, considera todas.
Saída: "<ext><TAB><arquivos><TAB><linhas>" e, no fim, "total<TAB><linhas>".
Exemplo: contar_linhas_codigo.sh src py sh
USO
}

case "${1:-}" in
  -h|--help) uso; exit 0 ;;
  "") echo "erro: informe a pasta" >&2; uso >&2; exit 1 ;;
esac
pasta="$1"; shift
if [[ ! -d "$pasta" ]]; then
  echo "erro: pasta inexistente: $pasta" >&2; exit 2
fi

declare -A soma=()
declare -A qtd=()
total=0
while IFS= read -r -d '' arq; do
  nome="$(basename "$arq")"
  [[ "$nome" == *.* ]] || continue
  ext="${nome##*.}"
  if (( $# > 0 )); then
    achou=0
    for e in "$@"; do
      if [[ "$e" == "$ext" ]]; then achou=1; fi
    done
    (( achou )) || continue
  fi
  n="$(grep -c '' "$arq" || true)"
  soma[$ext]=$(( ${soma[$ext]:-0} + n ))
  qtd[$ext]=$(( ${qtd[$ext]:-0} + 1 ))
  total=$((total + n))
done < <(find "$pasta" -type f -print0)

if (( ${#soma[@]} > 0 )); then
  for ext in $(printf '%s\n' "${!soma[@]}" | sort); do
    printf '%s\t%d\t%d\n' "$ext" "${qtd[$ext]}" "${soma[$ext]}"
  done
fi
printf 'total\t%d\n' "$total"
