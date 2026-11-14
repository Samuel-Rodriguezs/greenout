#!/usr/bin/env bash
# Renomeia em lote os arquivos de uma pasta aplicando uma expressão do sed.
# Uso: renomear_regex.sh [--dry-run] <pasta> <expressao_sed>
# Exemplo: renomear_regex.sh fotos 's/IMG_/foto_/'
# Saída: 0 ok, 1 uso, 2 pasta inexistente, 4 conflito de nome.
set -euo pipefail

uso() {
  cat <<'USO'
Uso: renomear_regex.sh [--dry-run] <pasta> <expressao_sed>
Aplica a expressão (ex.: 's/antigo/novo/') ao nome de cada arquivo da pasta.
Não sobrescreve arquivos existentes (sai com 4).
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
  echo "erro: informe pasta e expressão" >&2; uso >&2; exit 1
fi
pasta="${args[0]}"; expr="${args[1]}"
if [[ ! -d "$pasta" ]]; then
  echo "erro: pasta inexistente: $pasta" >&2; exit 2
fi
# valida a expressão
if ! echo teste | sed -E -e "$expr" >/dev/null 2>&1; then
  echo "erro: expressão sed inválida: $expr" >&2; exit 1
fi

n=0
while IFS= read -r -d '' arq; do
  nome="$(basename "$arq")"
  novo="$(printf '%s' "$nome" | sed -E -e "$expr")"
  if [[ "$novo" == "$nome" || -z "$novo" ]]; then continue; fi
  if [[ -e "$pasta/$novo" ]]; then
    echo "erro: conflito, já existe: $novo" >&2; exit 4
  fi
  if (( dry )); then
    echo "[dry-run] $nome -> $novo"
  else
    mv -- "$arq" "$pasta/$novo"
    echo "$nome -> $novo"
  fi
  n=$((n + 1))
done < <(find "$pasta" -maxdepth 1 -type f -print0 | sort -z)
echo "total: $n"
